import bpy

from ezdxf_exporter.data.color.ui import draw_preferences as draw_palette_aci
from ezdxf_exporter.data.layer.ui import draw_preferences as draw_layer
from ezdxf_exporter.data.unit.ui import draw_preferences as draw_unit

from .prop import Settings


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "ezdxf_exporter"

    category: bpy.props.EnumProperty(
        items=(
            ("palette_aci", "ACI Palette", ""),
            ("layer", "Layers", ""),
            ("unit", "Units", ""),
        )
    )
    settings: bpy.props.PointerProperty(type=Settings)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop_tabs_enum(self, "category")
        exec(f"draw_{self.category}(self.settings, layout.box())")
