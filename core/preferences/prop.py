import bpy

from ezdxf_exporter.data.color.prop import ColorPropertyGroup
from ezdxf_exporter.data.layer.prop import PreferencesSettings as LayerSettings
from ezdxf_exporter.data.unit.prop import PreferencesSettings as UnitSettings


class Settings(bpy.types.PropertyGroup):
    show_palette: bpy.props.BoolProperty(default=False, name="Show Palette")
    aci_palette: bpy.props.CollectionProperty(type=ColorPropertyGroup)
    layer: bpy.props.PointerProperty(type=LayerSettings)
    unit: bpy.props.PointerProperty(type=UnitSettings)
