import bpy

from ezdxf_exporter.data.color.prop import ColorPropertyGroup
from ezdxf_exporter.data.color.ui import draw_preferences as draw_palette

from ezdxf_exporter.data.layer.prop import PreferencesSettings as LayerSettings
from ezdxf_exporter.data.layer.ui import draw_preferences as draw_layer


def theme_box(layout, header):
    box = layout.box()
    box.label(text=header)
    return box


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "ezdxf_exporter"

    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")
    layer_preferences: bpy.props.PointerProperty(type=LayerSettings)

    def draw(self, context):
        layout = self.layout
        draw_palette(self, theme_box(layout, "ACI Palette"))
        draw_layer(self.layer_preferences, theme_box(layout, "Layers"))
