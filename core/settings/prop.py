import bpy
from bpy.props import (
    PointerProperty,
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from ezdxf_exporter.data.layer.prop import LayerSettings
from ezdxf_exporter.data.color.prop import ColorSettings
from ezdxf_exporter.data.choice.prop import DataSettings
from ezdxf_exporter.data.layer.prop import GlobalLayerSettings
from ezdxf_exporter.data.transform.prop import TransformSettings
from ezdxf_exporter.data.filter.prop import FilterSettings, ExportObjects, ExcludedObject
from ezdxf_exporter.data.text.prop import TextSettings
from ezdxf_exporter.data.unit.prop import PreferencesSettings as UnitSettings

from ezdxf_exporter.core.preferences.helper import get_preferences

from .ui import draw


class EntityProperties(bpy.types.PropertyGroup):
    layer: PointerProperty(
        name="Layer Props",
        type=LayerSettings,
    )
    color: PointerProperty(
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

    def set_default(self, context):
        prefs = get_preferences(context).settings.layer
        self.layer.entity_layer_prefix = prefs.layer_prefix
        self.layer.entity_layer_suffix = prefs.layer_suffix


class Settings(bpy.types.PropertyGroup):
    layer_global: PointerProperty(type=GlobalLayerSettings)
    choice: PointerProperty(type=DataSettings)
    transform: PointerProperty(type=TransformSettings)
    filter: PointerProperty(type=FilterSettings)
    # Note : The 1st element is the default settings if no entity overrides it
    entities: CollectionProperty(type=EntityProperties)
    text: PointerProperty(type=TextSettings)
    unit: PointerProperty(type=UnitSettings)

    def get_objects(self, context):
        export_setting = self.filter.export_objects
        exclude_setting = self.filter.export_excluded
        if export_setting == ExportObjects.SELECTED.value:
            return context.selected_objects
        elif export_setting == ExportObjects.SCENE.value:
            if exclude_setting == ExcludedObject.NONE:
                return [
                    o
                    for o in context.scene.objects
                    if not context.view_layer.layer_collection.children[o.users_collection[0].name].exclude
                    and not o.hide_viewport
                    and not o.hide_get()
                ]
            else:
                return context.scene.objects
        elif export_setting == ExportObjects.ALL.value:
            if exclude_setting == ExcludedObject.NONE:
                return [o for o in bpy.data.objects if not o.hide_viewport and not o.hide_get()]
            else:
                return bpy.data.objects

    def get_entity_settings(self, entity_type):
        if hasattr(entity_type, "__name__"):
            for setting in self.entities:
                if setting.id == entity_type.__name__:
                    if setting.use_default:
                        return self.default_entity
                    return setting
        return self.default_entity

    def draw(self, layout, context):
        draw(self, layout, context)

    @property
    def default_layer(self):
        return self.entities[0].layer

    @property
    def default_color(self):
        return self.entities[0].color

    @property
    def default_entity(self):
        return self.entities[0]
