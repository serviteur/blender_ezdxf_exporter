from typing import Dict
from enum import Enum
import ezdxf
import bpy
from ezdxf_exporter.data.filter.constants import ExcludedObject
from ezdxf_exporter.data.layer.constants import EntityLayer
from ezdxf_exporter.data.color.helper import get_material_color, get_object_color

from ezdxf_exporter.core.export.prop import DataExporter
from ezdxf_exporter.core.preferences.helper import get_preferences


def get_layer_collection(parent_col, search_name):
    found = None
    if parent_col.name == search_name:
        return parent_col
    for layer in parent_col.children:
        found = get_layer_collection(layer, search_name)
        if found:
            return found


class LayerExporter(DataExporter):
    KW_NAME = "name"
    KW_RGB = "rgb"
    KW_COLOR = "color"
    KW_TRANSPARENCY = "transparency"
    KW_FREEZE = "freeze"

    def populate_dxfattribs(
        self, obj: bpy.types.Object, dxfattribs: Dict[str, any], entity_type: Enum, override: bool = True
    ) -> bool:
        "Populates the 'Layer' key of dxfattribs dict, returns False if no layer should be created"
        dxfattribs["layer"] = self.get_or_create_layer_from_obj(obj, entity_type, override)
        return dxfattribs["layer"] is not None

    def sanitize_name(self, name):
        for char in ("/", "<", ">", "\\", "“", '"', ":", ";", "?", "*", "|", "=", "‘"):
            name = name.replace(char, "_")
        return name

    def create_layer(
        self, name: str, rgb=None, color=None, transparency: float = None, freeze: bool = False, override: bool = True
    ) -> ezdxf.entities.layer.Layer:
        "Create Layer and set properties if passed as parameters"
        layers = self.exporter.doc.layers

        name = self.sanitize_name(name)
        if name in layers:
            layer = layers.get(name)
            if not override:
                return layer
        else:
            layer = self.exporter.doc.layers.new(name)

        if rgb is not None:
            layer.rgb = rgb
        elif color is not None:
            layer.color = color
        if transparency is not None:
            layer.transparency = transparency
        if freeze:
            layer.freeze()
        return layer

    def get_or_create_layer_from_mat(self, mat: bpy.types.Material, override=True):
        rgb, a = get_material_color(mat)
        name = get_preferences(self.exporter.context).settings.layer.material_prefix + mat.name
        return self.create_layer(
            name,
            rgb,
            1 - a if self.exporter.settings.default_layer.entity_layer_transparency else 0,
            override=override,
        )

    def get_or_create_layer_from_obj(self, obj: bpy.types.Object, entity_type: Enum, override: bool = True) -> str:
        "Create the layer if needed and returns its name. Depends on the type of obj passed as parameter"
        exp = self.exporter
        context = exp.context
        exp_settings = exp.settings
        layer_settings = exp_settings.get_entity_settings(entity_type).layer
        layer_to = layer_settings.entity_layer_to
        prefix = layer_settings.entity_layer_prefix
        suffix = (
            get_preferences(exp.context).settings.layer.get_sub_layer_suffix(entity_type)
            if layer_settings.entity_layer_separate
            else ""
        )
        suffix += layer_settings.entity_layer_suffix

        settings = {}

        def update_settings_with_custom_props(obj):
            color = exp.color_exporter.get_color_from_custom_prop(
                obj, layer_settings.entity_layer_color_custom_prop_name
            )
            if color is None:
                pass
            elif isinstance(color, int):
                settings[self.KW_COLOR] = color
            else:
                settings[self.KW_RGB] = color[0:3]
                settings[self.KW_TRANSPARENCY] = 1 - color[3]

        if layer_to == EntityLayer.COLLECTION.value:
            coll = obj.users_collection[0]
            if coll is None:
                return None
            layer_coll = get_layer_collection(context.view_layer.layer_collection, coll.name)
            excluded_from_view_layer = layer_coll.exclude if layer_coll is not None else False
            col_exclude_state = exp_settings.filter.export_excluded
            if excluded_from_view_layer and col_exclude_state == ExcludedObject.NONE.value:
                return None
            settings[self.KW_NAME] = coll.name
            if layer_settings.entity_layer_color == "0":
                settings[self.KW_RGB] = exp.color_exporter._get_collection_color(coll)[0]
            elif layer_settings.entity_layer_color == "1":
                update_settings_with_custom_props(coll)
            settings[self.KW_FREEZE] = col_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer
        elif layer_to == EntityLayer.DATA_NAME.value:
            settings[self.KW_NAME] = obj.data.name
            if layer_settings.entity_layer_color == "1":
                update_settings_with_custom_props(obj.data)
        elif layer_to == EntityLayer.OBJECT_NAME.value:
            excluded_from_view_layer = obj.hide_get() or obj.hide_viewport
            obj_exclude_state = exp_settings.filter.export_excluded
            if excluded_from_view_layer and obj_exclude_state == ExcludedObject.NONE.value:
                return None

            if layer_settings.entity_layer_color == "0":
                rgb, a = get_object_color(obj)

                settings.update(
                    {
                        self.KW_NAME: obj.name,
                        self.KW_RGB: rgb,
                        self.KW_TRANSPARENCY: 1 - a if layer_settings.entity_layer_transparency else 0,
                        self.KW_FREEZE: obj_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer,
                    }
                )
            elif layer_settings.entity_layer_color == "1":
                update_settings_with_custom_props(obj)

        elif layer_to == EntityLayer.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            if mat is None:
                return None

            if layer_settings.entity_layer_color == "0":
                rgb, a = get_material_color(mat)

                settings.update(
                    {
                        self.KW_NAME: mat.name,
                        self.KW_RGB: rgb,
                        self.KW_TRANSPARENCY: 1 - a if layer_settings.entity_layer_transparency else 0,
                    }
                )
            elif layer_settings.entity_layer_color == "1":
                update_settings_with_custom_props(mat)

        elif layer_to == EntityLayer.SCENE_NAME.value:
            settings[self.KW_NAME] = context.scene.name
            if layer_settings.entity_layer_color == "1":
                update_settings_with_custom_props(context.scene)

        elif layer_to == EntityLayer.CUSTOM_PROP.value:
            settings[self.KW_NAME] = str(obj.get(layer_settings.entity_layer_to_custom, 0))
            
        elif layer_to == EntityLayer.CUSTOM.value:
            settings[self.KW_NAME] = layer_settings.entity_layer_to_custom

        layer = self.create_layer(
            name=prefix + settings.get(self.KW_NAME, "0") + suffix,
            rgb=settings.get(self.KW_RGB),
            color=settings.get(self.KW_COLOR),
            transparency=settings.get(self.KW_TRANSPARENCY),
            freeze=settings.get(self.KW_FREEZE),
            override=override,
        )
        return layer.dxf.name
