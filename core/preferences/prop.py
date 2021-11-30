import bpy

from ezdxf_exporter.data.color.prop import ColorPropertyGroup
from ezdxf_exporter.data.layer.prop import PreferencesSettings as LayerSettings


class Settings(bpy.types.PropertyGroup):
    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    layer: bpy.props.PointerProperty(type=LayerSettings)
