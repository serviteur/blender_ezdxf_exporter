from .ui import DXFEXPORTER_MT_Preset
from .operator import DXFEXPORTER_OT_Export
from bl_operators.presets import AddPresetBase
import bpy

# Preset System courtesy
# https://blender.stackexchange.com/questions/209877/preset-system-error
# https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/


class DXFEXPORTER_OT_Preset(bpy.types.Operator, AddPresetBase):
    """Save DXF Export Settings"""

    bl_idname = "dxf_exporter.preset"
    bl_label = "DXF Export Settings"
    preset_menu = DXFEXPORTER_MT_Preset.__name__

    # Variable used for all preset values
    preset_defines = ["op = bpy.context.active_operator"]

    # Properties to store in the preset
    preset_values = [f"op.{k}" for k in DXFEXPORTER_OT_Export.__annotations__.keys()]

    # Where to store the preset
    preset_subdir = DXFEXPORTER_OT_Export.bl_idname
