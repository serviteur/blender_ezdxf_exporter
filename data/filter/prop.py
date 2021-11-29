
import bpy
from .constants import ExportObjects, ExcludedObject
from .ui import draw

class MiscSettings(bpy.types.PropertyGroup):
    export_objects: bpy.props.EnumProperty(
        name="Export",
        description="Choose which objects to export",
        default=ExportObjects.SELECTED.value,
        items=[(e_o.value,) * 3 for e_o in ExportObjects],
    )

    export_excluded: bpy.props.EnumProperty(
        name="Excluded as",
        description="Choose how to export collections that are are excluded or hidden",
        default=ExcludedObject.FROZEN.value,
        items=[(e_c_t.value,) * 3 for e_c_t in ExcludedObject],
    )

    def draw(self, layout):
        draw(self, layout)