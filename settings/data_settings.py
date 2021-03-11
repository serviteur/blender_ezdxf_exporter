from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
    BoolVectorProperty,
)


NO_EXPORT = 'No Export'

class FaceType(Enum):
    NONE = NO_EXPORT
    MESH = 'MESH'
    FACES3D = '3DFACEs'
    POLYFACE = 'POLYFACE'


class LineType(Enum):
    NONE = NO_EXPORT
    LINES = 'LINEs'
    POLYLINES = 'POLYLINEs'


class PointType(Enum):
    NONE = NO_EXPORT
    POINTS = 'POINTs'


class TextType(Enum):
    NONE = NO_EXPORT
    MTEXT = 'MText'
    TEXT = 'Text'
    MESH = 'Mesh'


class CurveType(Enum):
    NONE = NO_EXPORT
    SPLINE = 'Spline'
    MESH = 'Mesh'


class EmptyType(Enum):
    NONE = NO_EXPORT
    BLOCK = 'Block'
    POINT = 'POINT'
    # TODO Export Empty as its viewport Geometry ?


class CameraType(Enum):
    NONE = NO_EXPORT
    VIEWPORT = 'VIEWPORT (Paperspace)'
    VPORT = 'VPORT (Modelspace)'
    VIEW = 'VIEW (Modelspace)'


class DataSettings(PropertyGroup):
    sub_layers_suffixes = {
        FaceType: "FACES",
        LineType: "LINES",
        PointType: "POINTS",
        TextType: "TEXTS",
        EmptyType: "EMPTIES",
        CameraType: "VIEW",
    }

    faces_export: EnumProperty(
        name="Export Faces",
        default=FaceType.MESH.value,
        items=[(f_t.value,)*3 for f_t in FaceType])

    lines_export: EnumProperty(
        name="Export Lines",
        default=LineType.NONE.value,
        items=[(l_t.value,)*3 for l_t in LineType])

    points_export: EnumProperty(
        name="Export Points",
        default=PointType.NONE.value,
        items=[(p_t.value,)*3 for p_t in PointType])

    texts_export: EnumProperty(
        name="Export Texts",
        default=TextType.MTEXT.value,
        items=[(t_t.value,)*3 for t_t in TextType])

    empties_export: EnumProperty(
        name="Export Empties",
        default=EmptyType.NONE.value,
        items=[(e_t.value,)*3 for e_t in EmptyType])

    cameras_export: EnumProperty(
        name="Export Cameras",
        default=CameraType.VIEWPORT.value,
        items=[(c_t.value,)*3 for c_t in CameraType])

    entity_link: BoolVectorProperty(
        name="Use Exporter settings",
        description="Use Exporter settings for exported entities if ON, else use default ones",
        size=6,
        default=(True,) * 6
    )

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities",
        default=True,
    )

    def draw(self, layout, objects):
        layout.label(text="Export Data")
        geometry_box = layout.box()
        col = geometry_box.column(align=True)
        lookup_type_dic = {}
        for obj in objects:
            lookup_type_dic[obj.type] = True
        i = -1
        for prop, name, _type in (
            ("faces_export", "Faces", 'MESH'),
            ("lines_export", "Edges", 'MESH'),
            ("points_export", "Vertices", 'MESH'),
            ("texts_export", "Texts", 'FONT'),
            ("empties_export", "Empties", 'EMPTY'),
            ("cameras_export", "Cameras", 'CAMERA'),
        ):
            i += 1
            if lookup_type_dic.get(_type) is None:
                continue
            geom_split = col.split(factor=0.25, align=True)
            geom_split.label(text=name)
            geom_split = geom_split.split(factor=0.9, align=True)
            geom_split.prop(self, prop, text="")
            link = geom_split.row(align=True)
            link.prop(self, "entity_link", index=i, text="",
                      icon='LINKED' if self.entity_link[i] else 'UNLINKED')
            # NONE.value is the same for all entity enums
            link.active = getattr(self, prop) != TextType.NONE.value
        geometry_box.prop(self, "use_blocks")

    def get_sub_layer_suffix(self, entity_type):
        # TODO : Add customization in addonprefs
        suffix = self.sub_layers_suffixes.get(entity_type, "")
        return suffix if suffix == "" else ("_" + suffix)