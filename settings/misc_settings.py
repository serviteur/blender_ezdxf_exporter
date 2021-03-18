from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
)
from .__init__ import NO_EXPORT


class ExcludedObject(Enum):
    NONE = NO_EXPORT
    THAWED = "Thawed"
    FROZEN = "Frozen"


class ExportObjects(Enum):
    SELECTED = "Only Selected"
    SCENE = "Current Scene"
    # VIEW_LAYER = "Current View Layer"
    ALL = "All Objects in file"


class MiscSettings(PropertyGroup):
    export_objects: EnumProperty(
        name="Export",
        description="Choose which objects to export",
        default=ExportObjects.SELECTED.value,
        items=[(e_o.value,) * 3 for e_o in ExportObjects],
    )

    export_excluded: EnumProperty(
        name="Excluded as",
        description="Choose how to export collections that are are excluded or hidden",
        default=ExcludedObject.FROZEN.value,
        items=[(e_c_t.value,) * 3 for e_c_t in ExcludedObject],
    )

    def draw(self, layout):        
        layout.label(text="Miscellaneous")
        misc_box = layout.box()
        col = misc_box.column(align=True)
        split = col.split(factor=0.3)
        split.label(text="Export")
        split.prop(self, "export_objects", text="")
        split = col.split(factor=0.3)
        split.label(text="Excluded as")
        split.prop(self, "export_excluded", text="")
        split.active = self.export_objects != ExportObjects.SELECTED.value