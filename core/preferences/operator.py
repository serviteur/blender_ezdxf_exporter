import bpy
from ezdxf_exporter.data.color.constants import ACI_RGB_MAPPING


class DXFEXPORTER_OT_generate_aci_palette(bpy.types.Operator):
    bl_idname = "dxf_exporter.generate_aci_palette"
    bl_label = "Generate ACI Palette"

    def execute(self, context):
        prefs = context.preferences.addons["ezdxf_exporter"].preferences
        palette = prefs.aci_palette
        palette.clear()
        for c in ACI_RGB_MAPPING:
            new_color = palette.add()
            new_color["value"] = c
        return {"FINISHED"}