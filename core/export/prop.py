import bpy
from bpy.props import (
    PointerProperty,
    StringProperty,
    BoolProperty,
)
from ezdxf_exporter.data.layer.prop import LayerSettings
from ezdxf_exporter.data.color.prop import ColorSettings


class DataExporter:
    def __init__(self, exporter) -> None:
        self.exporter = exporter


class EntityProperties(bpy.types.PropertyGroup):
    layer_settings: PointerProperty(
        name="Layer Props",
        type=LayerSettings,
    )
    color_settings: PointerProperty(
        name="Color Props",
        type=ColorSettings,
    )
    id: StringProperty(
        name="Data identifier",
        description="Unique string identifier (enum class __name__)",
    )
    use_default: BoolProperty(
        name="Use default settings",
        default=True,
    )
