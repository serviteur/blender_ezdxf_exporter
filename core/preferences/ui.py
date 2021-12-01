import bpy

from ezdxf_exporter.data.color.ui import draw_preferences as draw_palette
from ezdxf_exporter.data.layer.ui import draw_preferences as draw_layer
from ezdxf_exporter.data.unit.ui import draw_preferences as draw_unit

from .prop import Settings


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "ezdxf_exporter"

    category: bpy.props.EnumProperty(
        items=(
            ("ACI Palette",) * 3,
            ("Layers",) * 3,
        )
    )
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")
    settings: bpy.props.PointerProperty(type=Settings)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop_tabs_enum(self, "category")
        if self.category == "ACI Palette":
            draw_palette(self, layout.box())
        elif self.category == "Layers":
            draw_layer(self.settings.layer, layout.box())
