# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Iterator,
    Optional,
    List,
    Dict,
    cast,
    Union,
    Generic,
    TypeVar,
)
from collections import OrderedDict
import logging

from ezdxf.audit import Auditor, AuditError
from ezdxf.lldxf import const, validator
from ezdxf.entities.table import TableHead
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter,
        EntityDB,
        Drawing,
        DXFEntity,
        Layer,
        Linetype,
        Textstyle,
        VPort,
        View,
        AppID,
        UCSTableEntry,
        BlockRecord,
        DimStyle,
    )

logger = logging.getLogger("ezdxf")

T = TypeVar("T", bound="DXFEntity")


class Table(Generic[T]):
    TABLE_TYPE = "UNKNOWN"

    def __init__(self):
        self.doc: Optional["Drawing"] = None
        self.entries: Dict[str, T] = OrderedDict()
        self._head = TableHead()

    def load(self, doc: "Drawing", entities: Iterator["DXFEntity"]) -> None:
        """Loading interface. (internal API)"""
        self.doc = doc
        table_head = next(entities)
        if isinstance(table_head, TableHead):
            self._head = table_head
        else:
            raise const.DXFStructureError(
                "Critical structure error in TABLES section."
            )
        expected_entry_dxftype = self.TABLE_TYPE
        for table_entry in entities:
            if table_entry.dxftype() == expected_entry_dxftype:
                self._append(cast(T, table_entry))
            else:
                logger.warning(
                    f"Ignored invalid DXF entity type '{table_entry.dxftype()}'"
                    f" in {self.TABLE_TYPE} table."
                )

    def reset(self, doc: "Drawing", handle: str) -> None:
        """Reset table. (internal API)"""
        self.doc = doc
        self._set_head(self.TABLE_TYPE, handle)
        self.entries.clear()

    def _set_head(self, name: str, handle: str = None) -> None:
        self._head = TableHead.new(
            handle, owner="0", dxfattribs={"name": name}, doc=self.doc
        )

    @property
    def head(self):
        """Returns table head entry."""
        return self._head

    @property
    def name(self) -> str:
        return self.TABLE_TYPE

    @staticmethod
    def key(name: str) -> str:
        """Unified table entry key."""
        return validator.make_table_key(name)

    def has_entry(self, name: str) -> bool:
        """Returns ``True`` if an table entry `name` exist."""
        return self.key(name) in self.entries

    __contains__ = has_entry

    def __len__(self) -> int:
        """Count of table entries."""
        return len(self.entries)

    def __iter__(self) -> Iterator[T]:
        """Iterable of all table entries."""
        for e in self.entries.values():
            if e.is_alive:
                yield e

    def new(self, name: str, dxfattribs: dict = None) -> T:
        """Create a new table entry `name`.

        Args:
            name: name of table entry, case insensitive
            dxfattribs: additional DXF attributes for table entry

        """
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f"{self.TABLE_TYPE} '{name}' already exists!"
            )
        dxfattribs = dxfattribs or {}
        dxfattribs["name"] = name
        dxfattribs["owner"] = self._head.dxf.handle
        return self.new_entry(dxfattribs)

    def get(self, name: str) -> T:
        """Get table entry `name` (case insensitive).
        Raises :class:`DXFValueError` if table entry does not exist.
        """
        key = self.key(name)
        entry = self.entries.get(key, None)
        if entry:
            return entry
        else:
            raise const.DXFTableEntryError(name)

    def remove(self, name: str) -> None:
        """Removes table entry `name`. Raises :class:`DXFValueError`
        if table-entry does not exist.
        """
        key = self.key(name)
        entry = self.get(name)
        self.entitydb.delete_entity(entry)
        self.discard(key)

    def duplicate_entry(self, name: str, new_name: str) -> T:
        """Returns a new table entry `new_name` as copy of `name`,
        replaces entry `new_name` if already exist.

        Raises:
             DXFValueError: `name` does not exist

        """
        entry = self.get(name)
        entitydb = self.entitydb
        if entitydb:
            new_entry = entitydb.duplicate_entity(entry)
        else:  # only for testing!
            new_entry = entry.copy()
        new_entry.dxf.name = new_name
        entry = cast(T, new_entry)
        self._append(entry)
        return entry

    def discard(self, name: str) -> None:
        """Remove table entry without destroying object. (internal API)"""
        del self.entries[self.key(name)]

    def replace(self, name: str, entry: T) -> None:
        """Replace table entry `name` by new `entry`. (internal API)"""
        self.discard(name)
        self._append(entry)

    @property
    def entitydb(self) -> "EntityDB":
        return self.doc.entitydb  # type: ignore

    def new_entry(self, dxfattribs: dict) -> T:
        """Create and add new table-entry of type 'self.entry_dxftype'.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        assert self.doc is not None, "valid DXF document expected"
        entry = cast(
            T, factory.create_db_entry(self.TABLE_TYPE, dxfattribs, self.doc)
        )

        self._append(entry)
        return entry

    def _append(self, entry: T) -> None:
        """Add a table entry, replaces existing entries with same name.
        (internal API).
        """
        assert entry.dxftype() == self.TABLE_TYPE
        self.entries[self.key(entry.dxf.name)] = entry

    def add_entry(self, entry: T) -> None:
        """Add a table `entry`, created by other object than this table.
        (internal API)
        """
        if entry.dxftype() != self.TABLE_TYPE:
            raise const.DXFTypeError(
                f"Invalid table entry type {entry.dxftype()} "
                f"for table {self.TABLE_TYPE}"
            )
        name = entry.dxf.name
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f"{self._head.dxf.name} {name} already exists!"
            )
        entry.doc = self.doc
        entry.dxf.owner = self._head.dxf.handle
        self._append(entry)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        """Export DXF representation. (internal API)"""

        def prologue():
            self.update_owner_handles()
            # The table head itself has no owner and is therefore always '0':
            self._head.dxf.owner = "0"
            self._head.dxf.count = len(self)
            self._head.export_dxf(tagwriter)

        def content():
            for entry in self.entries.values():
                # VPORT
                if isinstance(entry, list):
                    for e in entry:
                        e.export_dxf(tagwriter)
                else:
                    entry.export_dxf(tagwriter)

        def epilogue():
            tagwriter.write_tag2(0, "ENDTAB")

        prologue()
        content()
        epilogue()

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entry in self.entries.values():
            entry.dxf.owner = owner_handle

    def set_handle(self, handle: str):
        """Set new `handle` for table, updates also :attr:`owner` tag of table
        entries. (internal API)
        """
        if self._head.dxf.handle is None:
            self._head.dxf.handle = handle
            self.update_owner_handles()

    def audit(self, auditor: Auditor):
        # The table entries are stored in the entity database and are already
        # audited!
        self._fix_table_head(auditor)
        self._fix_entry_handles(auditor)

    def _fix_entry_handles(self, auditor: Auditor):
        # Why: see duplicate handle issue #604
        entitydb = self.entitydb
        for entry in self:
            entity = entitydb.get(entry.dxf.handle)
            if entity is not entry:  # duplicate handle usage
                # This can break entities referring to this entity, but at
                # least the DXF readable
                entry.dxf.handle = entitydb.next_handle()
                self.entitydb.add(entry)
                auditor.fixed_error(
                    code=AuditError.INVALID_TABLE_HANDLE,
                    message=f"Fixed invalid table entry handle in {entry}",
                )

    def _fix_table_head(self, auditor: Auditor):
        def fix_head():
            head.dxf.handle = entitydb.next_handle()
            entitydb.add(head)
            if log:
                auditor.fixed_error(
                    code=AuditError.INVALID_TABLE_HANDLE,
                    message=f"Fixed invalid table head handle in table {self.name}",
                )

        # fix silently for older DXF versions
        log = auditor.doc.dxfversion > const.DXF12

        head = self.head
        # Another exception for an invalid owner tag, but this usage is
        # covered in Auditor.check_owner_exist():
        head.dxf.owner = "0"
        handle = head.dxf.handle
        entitydb = self.entitydb
        if handle is None or handle == "0":
            # Entity database does not assign new handle:
            fix_head()
        else:
            # Why: see duplicate handle issue #604
            entry = self.entitydb.get(handle)
            if entry is not head:  # another entity has the same handle!
                fix_head()
        # Just to be sure owner handle is valid in every circumstance:
        self.update_owner_handles()


class LayerTable(Table["Layer"]):
    TABLE_TYPE = "LAYER"

    def new_entry(self, dxfattribs: dict) -> "Layer":
        layer = cast("Layer", super().new_entry(dxfattribs))
        if self.doc:
            layer.set_required_attributes()
        return layer

    def add(
        self,
        name: str,
        *,
        color: int = const.BYLAYER,
        true_color: int = None,
        linetype: str = "Continuous",
        lineweight: int = const.LINEWEIGHT_BYLAYER,
        plot: bool = True,
        transparency: Optional[float] = None,
        dxfattribs: Dict = None,
    ) -> "Layer":
        """Add a new :class:`~ezdxf.entities.Layer`.

        Args:
            name (str): layer name
            color (int): :ref:`ACI` value, default is BYLAYER
            true_color (int): true color value, use :func:`ezdxf.rgb2int` to
                create ``int`` values from RGB values
            linetype (str): line type name, default is "Continuous"
            lineweight (int): line weight, default is BYLAYER
            plot (bool): plot layer as bool, default is ``True``
            transparency: transparency value in the range [0, 1], where 1 is
                100% transparent and 0 is opaque
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        if validator.is_valid_aci_color(color):
            dxfattribs["color"] = color
        else:
            raise const.DXFValueError(f"invalid color: {color}")
        dxfattribs["linetype"] = linetype
        if validator.is_valid_lineweight(lineweight):
            dxfattribs["lineweight"] = lineweight
        else:
            raise const.DXFValueError(f"invalid lineweight: {lineweight}")
        if true_color is not None:
            dxfattribs["true_color"] = int(true_color)
        dxfattribs["plot"] = int(plot)
        layer = cast("Layer", self.new(name, dxfattribs))
        if transparency is not None:
            layer.transparency = transparency
        return layer


class LinetypeTable(Table["Linetype"]):
    TABLE_TYPE = "LTYPE"

    def new_entry(self, dxfattribs: dict) -> T:
        pattern = dxfattribs.pop("pattern", [0.0])
        length = dxfattribs.pop("length", 0)  # required for complex types
        ltype = cast("Linetype", super().new_entry(dxfattribs))
        ltype.setup_pattern(pattern, length)
        return cast(T, ltype)

    def add(
        self,
        name: str,
        pattern: Union[List[float], str],
        *,
        description: str = "",
        length: float = 0.0,
        dxfattribs: Dict = None,
    ) -> "Linetype":
        """Add a new line type entry. The simple line type pattern is a list of
        floats :code:`[total_pattern_length, elem1, elem2, ...]`
        where an element > 0 is a line, an element < 0 is a gap and  an
        element == 0.0 is a dot. The definition for complex line types are
        strings, like: ``'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25'``
        similar to the line type definitions stored in the line definition
        `.lin` files, for more information see the tutorial about complex line
        types. Be aware that not many CAD applications and DXF viewers support
        complex linetypes.

        .. seealso::

            - `Tutorial for simple line types <https://ezdxf.mozman.at/docs/tutorials/linetypes.html>`_
            - `Tutorial for complex line types <https://ezdxf.mozman.at/docs/tutorials/linetypes.html#tutorial-for-complex-linetypes>`_

        Args:
            name (str): line type  name
            pattern: line type pattern as list of floats or as a string
            description (str): line type description, optional
            length (float): total pattern length, only for complex line types required
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": name,
                "description": str(description),
                "pattern": pattern,
                "length": float(length),
            }
        )
        return self.new_entry(dxfattribs)  # type: ignore


class TextstyleTable(Table["Textstyle"]):
    TABLE_TYPE = "STYLE"

    def add(
        self, name: str, *, font: str, dxfattribs: Dict = None
    ) -> "Textstyle":
        """Add a new text style entry for TTF fonts. The entry must not yet
        exist, otherwise an :class:`DXFTableEntryError` exception will be
        raised.

        Finding the TTF font files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            name (str): text style name
            font (str): TTF font file name like "Arial.ttf", the real font file
                name from the file system is required and remember only Windows
                is case insensitive.
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": name,
                "font": str(font),
                "last_height": 2.5,  # maybe required by AutoCAD
            }
        )
        return self.new_entry(dxfattribs)

    def add_shx(self, shx_file: str, *, dxfattribs: Dict = None) -> "Textstyle":
        """Add a new shape font (SHX file) entry. These are special text style
        entries and have no name. The entry must not yet exist, otherwise an
        :class:`DXFTableEntryError` exception will be raised.

        Finding the SHX files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            shx_file (str): shape file name like "gdt.shx"
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        if self.find_shx(shx_file) is not None:
            raise const.DXFTableEntryError(
                f"{self._head.dxf.name} shape file entry for "
                f"'{shx_file}' already exists!"
            )

        dxfattribs = dict(dxfattribs or {})
        dxfattribs.update(
            {
                "name": "",  # shape file entry has no name
                "flags": 1,  # shape file flag
                "font": shx_file,
                "last_height": 2.5,  # maybe required by AutoCAD
            }
        )
        return self.new_entry(dxfattribs)

    def get_shx(self, shx_file: str) -> "Textstyle":
        """Get existing entry for a shape file (SHX file), or create a new
        entry.

        Finding the SHX files is the task of the DXF viewer and each
        viewer is different (hint: support files).

        Args:
            shx_file (str): shape file name like "gdt.shx"

        """
        shape_file = self.find_shx(shx_file)
        if shape_file is None:
            return self.add_shx(shx_file)
        return shape_file

    def find_shx(self, shx_file: str) -> Optional["Textstyle"]:
        """Find the shape file (SHX file) text style table entry, by a case
        insensitive search.

        A shape file table entry has no name, so you have to search by the
        font attribute.

        Args:
            shx_file (str): shape file name like "gdt.shx"

        """
        lower_name = shx_file.lower()
        for entry in iter(self):
            if entry.dxf.font.lower() == lower_name:
                return entry
        return None


class ViewportTable(Table["VPort"]):
    TABLE_TYPE = "VPORT"
    # Viewport-Table can have multiple entries with same name
    # each table entry is a list of VPORT entries

    def new(self, name: str, dxfattribs: dict = None) -> T:
        """Create a new table entry."""
        dxfattribs = dxfattribs or {}
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)

    def add(self, name: str, *, dxfattribs: Dict = None) -> "VPort":
        """Add a new modelspace viewport entry. A modelspace viewport
        configuration can consist of multiple viewport entries with the same
        name.

        Args:
            name (str): viewport name, multiple entries possible
            dxfattribs (dict): additional DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)

    def remove(self, name: str) -> None:
        """Remove table-entry from table and entitydb by name."""
        key = self.key(name)
        entries = cast(List["DXFEntity"], self.get(name))
        for entry in entries:
            self.entitydb.delete_entity(entry)
        del self.entries[key]

    def __iter__(self) -> Iterator[T]:
        for entries in self.entries.values():
            yield from iter(entries)  # type: ignore

    def _flatten(self) -> Iterator[T]:
        for entries in self.entries.values():
            yield from iter(entries)  # type: ignore

    def __len__(self):
        # calling __iter__() invokes recursion!
        return len(list(self._flatten()))

    def new_entry(self, dxfattribs: dict) -> T:
        """Create and add new table-entry of type 'self.entry_dxftype'.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        assert self.doc is not None, "valid DXF document expected"
        entry = cast(
            T, factory.create_db_entry(self.TABLE_TYPE, dxfattribs, self.doc)
        )
        self._append(entry)
        return entry

    def duplicate_entry(self, name: str, new_name: str) -> T:
        raise NotImplementedError()

    def _append(self, entry: T) -> None:
        key = self.key(entry.dxf.name)
        if key in self.entries:
            self.entries[key].append(entry)  # type: ignore
        else:
            self.entries[key] = [entry]  # type: ignore # store list of VPORT

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entries in self.entries.values():
            for entry in entries:  # type: ignore
                entry.dxf.owner = owner_handle

    def get_config(self, name: str) -> List["VPort"]:
        """Returns a list of :class:`~ezdxf.entities.VPort` objects, for
        the multi-viewport configuration `name`.
        """
        try:
            return self.entries[self.key(name)]  # type: ignore
        except KeyError:
            raise const.DXFTableEntryError(name)

    def delete_config(self, name: str) -> None:
        """Delete all :class:`~ezdxf.entities.VPort` objects of the
        multi-viewport configuration `name`.
        """
        self.remove(name)


class AppIDTable(Table["AppID"]):
    TABLE_TYPE = "APPID"

    def add(self, name: str, *, dxfattribs: Dict = None) -> "AppID":
        """Add a new appid table entry.

        Args:
            name (str): appid name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)


class ViewTable(Table["View"]):
    TABLE_TYPE = "VIEW"

    def add(self, name: str, *, dxfattribs: Dict = None) -> "View":
        """Add a new view table entry.

        Args:
            name (str): view name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)


class BlockRecordTable(Table["BlockRecord"]):
    TABLE_TYPE = "BLOCK_RECORD"

    def add(self, name: str, *, dxfattribs: Dict = None) -> "BlockRecord":
        """Add a new block record table entry.

        Args:
            name (str): block record name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)


class DimStyleTable(Table["DimStyle"]):
    TABLE_TYPE = "DIMSTYLE"

    def add(self, name: str, *, dxfattribs: Dict = None) -> "DimStyle":
        """Add a new dimension style table entry.

        Args:
            name (str): dimension style name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)


class UCSTable(Table["UCSTableEntry"]):
    TABLE_TYPE = "UCS"

    def add(self, name: str, *, dxfattribs: Dict = None) -> "UCSTableEntry":
        """Add a new UCS table entry.

        Args:
            name (str): UCS name
            dxfattribs (dict): DXF attributes

        .. versionadded:: 0.17

        """
        dxfattribs = dict(dxfattribs or {})
        dxfattribs["name"] = name
        return self.new_entry(dxfattribs)
