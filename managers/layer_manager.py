from typing import Dict
from enum import Enum
from bpy.types import (
    Material,
    Object,
    Collection,
    Context,
)
import ezdxf
from ..settings.layer_settings import (
    EntityLayer,
)
from ..settings.misc_settings import (
    ExcludedObject,
)
from .manager import Manager


def get_layer_collection(parent_col, search_name):
    found = None
    if parent_col.name == search_name:
        return parent_col
    for layer in parent_col.children:
        found = get_layer_collection(layer, search_name)
        if found:
            return found


class LayerManager(Manager):
    KW_NAME = 'name'
    KW_RGB = 'rgb'
    KW_TRANSPARENCY = 'transparency'
    KW_FREEZE = 'freeze'

    def populate_dxfattribs(self, obj: Object, dxfattribs: Dict[str, any], entity_type: Enum, override: bool = True) -> bool:
        "Populates the 'Layer' key of dxfattribs dict, returns False if no layer should be created"
        dxfattribs['layer'] = self.get_or_create_layer(
            obj, entity_type, override)
        return dxfattribs['layer'] is not None

    def create_layer(self, name: str, rgb=None, transparency: float = None, freeze: bool = False) -> ezdxf.entities.layer.Layer:
        "Create Layer and set properties if passed as parameters"
        layers = self.exporter.doc.layers
        if name in layers:
            layer = layers.get(name)
        else:
            layer = self.exporter.doc.layers.new(name)
        if rgb is not None:
            layer.rgb = rgb
        if transparency is not None:
            layer.transparency = transparency
        if freeze:
            layer.freeze()
        return layer

    def get_or_create_layer(self, obj: Object, entity_type: Enum, override: bool = True):
        "Create the layer if needed and returns its name. Depends on the type of obj passed as parameter"
        exp = self.exporter
        context = exp.context
        exp_settings = exp.settings
        layer_settings = exp_settings.get_entity_settings(
            entity_type).layer_settings
        layer_to = layer_settings.entity_layer_to
        prefix = layer_settings.entity_layer_prefix
        suffix = exp_settings.data_settings.get_sub_layer_suffix(
            entity_type) if layer_settings.entity_layer_separate else ""
        suffix += layer_settings.entity_layer_suffix

        settings = {}
        if layer_to == EntityLayer.COLLECTION.value:
            coll = obj.users_collection[0]
            if coll is None:
                return None
            layer_name = coll.name
            layer_coll = get_layer_collection(
                context.view_layer.layer_collection, layer_name)
            excluded_from_view_layer = layer_coll.exclude if layer_coll is not None else False
            col_exclude_state = exp_settings.misc_settings.export_excluded
            if excluded_from_view_layer and col_exclude_state == ExcludedObject.NONE.value:
                return None
            settings.update({
                self.KW_NAME: layer_name,
                self.KW_RGB: exp.color_mgr._get_collection_color(coll)[0],
                self.KW_FREEZE: col_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer
            })
        elif layer_to == EntityLayer.DATA_NAME.value:
            settings[self.KW_NAME] = obj.data.name
        elif layer_to == EntityLayer.OBJECT_NAME.value:
            excluded_from_view_layer = obj.hide_get() or obj.hide_viewport
            obj_exclude_state = exp_settings.misc_settings.export_excluded
            if excluded_from_view_layer and obj_exclude_state == ExcludedObject.NONE.value:
                return None
            rgb, a = exp.color_mgr._get_object_color(obj)

            settings.update({
                self.KW_NAME: obj.name,
                self.KW_RGB: rgb,
                self.KW_TRANSPARENCY: 1 - a if layer_settings.entity_layer_transparency else 0,
                self.KW_FREEZE: obj_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer
            })
        elif layer_to == EntityLayer.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            if mat is None:
                return None
            rgb, a = exp.color_mgr._get_material_color(mat)

            settings.update({
                self.KW_NAME: mat.name,
                self.KW_RGB: rgb,
                self.KW_TRANSPARENCY: 1 - a if layer_settings.entity_layer_transparency else 0,
            })
        elif layer_to == EntityLayer.SCENE_NAME.value:
            settings[self.KW_NAME] = context.scene.name

        layers = exp.doc.layers
        layer_name = prefix + settings.get(self.KW_NAME, "0") + suffix
        if override or layer_name not in layers:
            self.create_layer(
                layer_name,
                settings.get(self.KW_RGB),
                settings.get(self.KW_TRANSPARENCY),
                settings.get(self.KW_FREEZE))
        return layer_name
