import bpy
from ezdxf_exporter.core.preferences.prop import ColorPropertyGroup


class DXFEXPORTERAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "ezdxf_exporter"

    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")

    def draw(self, context):
        layout = self.layout

        layout.operator("dxf_exporter.generate_aci_palette", text="Regenerate ACI Palette")
        if self.aci_palette:
            layout.prop(self, "show_palette", toggle=True, text=("Hide" if self.show_palette else "Show") + " Palette")
            if self.show_palette:
                grid_even = layout.grid_flow(row_major=True, align=True, columns=10)
                grid_odd = layout.grid_flow(row_major=True, align=True, columns=10)
                for i, pg in enumerate(self.aci_palette):
                    if i > 10 and i % 2:
                        grid_odd.prop(pg, "value", text=str(i))
                    else:
                        grid_even.prop(pg, "value", text=str(i))
