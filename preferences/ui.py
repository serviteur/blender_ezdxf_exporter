import bpy
from blender_ezdxf_exporter.settings.color_settings import ACI_RGB_MAPPING


class DXFEXPORTER_OT_generate_aci_palette(bpy.types.Operator):
    bl_idname = "dxf_exporter.generate_aci_palette"
    bl_label = "Generate ACI Palette"

    def execute(self, context):
        prefs = context.preferences.addons["blender_ezdxf_exporter"].preferences
        palette = prefs.aci_palette
        palette.clear()
        for c in ACI_RGB_MAPPING:
            new_color = palette.add()
            new_color.value = c
        return {"FINISHED"}


def set_prop(self, value):
    if self.readonly:
        return
    self["value"] = value
    self.readonly = True


def get_prop(self):
    return self["value"]


class ColorPropertyGroup(bpy.types.PropertyGroup):
    value: bpy.props.FloatVectorProperty(subtype="COLOR", set=set_prop, get=get_prop, min=0, max=1)
    readonly: bpy.props.BoolProperty()


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "blender_ezdxf_exporter"

    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")

    def draw(self, context):
        layout = self.layout
        layout.operator("dxf_exporter.generate_aci_palette", text="Regenerate ACI Palette")
        layout.prop(self, "show_palette", toggle=True, text=("Hide" if self.show_palette else "Show") + " Palette")
        if self.show_palette:
            grid_even = layout.grid_flow(row_major=True, align=True, columns=10)
            grid_odd = layout.grid_flow(row_major=True, align=True, columns=10)
            for i, pg in enumerate(self.aci_palette):
                if i > 10 and i % 2:
                    grid_odd.prop(pg, "value", text=str(i))
                else:
                    grid_even.prop(pg, "value", text=str(i))
