import bpy

from ezdxf_exporter.data.color.prop import ColorPropertyGroup
from ezdxf_exporter.data.color.ui import draw_preferences as draw_palette

from ezdxf_exporter.data.layer.prop import PreferencesSettings as LayerSettings
from ezdxf_exporter.data.layer.ui import draw_preferences as draw_layer


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "ezdxf_exporter"

    category: bpy.props.EnumProperty(
        items=(
            ("ACI Palette",) * 3,
            ("Layers",) * 3,
        )
    )
    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")
    layer_preferences: bpy.props.PointerProperty(type=LayerSettings)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop_tabs_enum(self, "category")
        if self.category == "ACI Palette":
            draw_palette(self, layout.box())
        elif self.category == "Layers":
            draw_layer(self.layer_preferences, layout.box())
