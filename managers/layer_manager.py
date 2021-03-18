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


class LayerManager(Manager):
    def populate_dxfattribs(self, obj: Object, dxfattribs: Dict[str, any], entity_type: Enum, override: bool = True) -> bool:
        "Populates the 'Layer' key of dxfattribs dict, returns False if no layer should be created"
        dxfattribs['layer'] = self.get_or_create_layer(
            obj, entity_type, override)
        return dxfattribs['layer'] is not None

    def create_layer(self, name: str, rgb=None, transparency: float = None, freeze: bool = False) -> ezdxf.entities.layer.Layer:
        "Create Layer and set properties if passed as parameters"
        layer = self.exporter.doc.layers.new(name)
        if rgb is not None:
            layer.rgb = rgb
        if transparency is not None:
            layer.transparency = transparency
        if freeze:
            layer.freeze()
        return layer

    def get_or_create_layer_from_material(self, mat: Material, layer_settings, prefix=None, suffix=None, ) -> str:
        if prefix is None:
            prefix = ""
        if suffix is None:
            suffix = ""
        if mat is None:
            return None
        exp = self.exporter
        layers = exp.doc.layers
        layer_name = prefix + mat.name + suffix
        if layer_name not in layers:
            rgb, a = exp.color_mgr._get_material_color(mat)
            self.create_layer(
                layer_name,
                rgb,
                1 - a if layer_settings.entity_layer_transparency else 0)
        return layer_name

    def get_or_create_layer_from_collection(self, coll: Collection, suffix: str, override: bool):
        exp = self.exporter
        context = exp.context
        layers = exp.doc.layers
        layer_name = coll.name + suffix
        excluded_from_view_layer = context.view_layer.layer_collection.children[
            coll.name].exclude
        col_exclude_state = exp.settings.misc_settings.export_excluded
        if excluded_from_view_layer and col_exclude_state == ExcludedObject.NONE.value:
            return None
        if override and layer_name not in layers:
            self.create_layer(
                layer_name,
                rgb=exp.color_mgr._get_collection_color(coll)[0],
                freeze=col_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer)
        return layer_name

    def get_or_create_layer_from_object(self, obj, suffix, override, layer_settings):
        exp = self.exporter
        layers = exp.doc.layers
        layer_name = obj.name + suffix
        excluded_from_view_layer = obj.hide_get() or obj.hide_viewport
        obj_exclude_state = exp.settings.misc_settings.export_excluded
        if excluded_from_view_layer and obj_exclude_state == ExcludedObject.NONE.value:
            return None
        if override and layer_name not in layers:
            rgb, a = exp.color_mgr._get_object_color(obj)
            self.create_layer(
                layer_name,
                rgb=rgb,
                transparency=1 - a if layer_settings.entity_layer_transparency else 0,
                freeze=obj_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer)
            return layer_name

    def get_or_create_layer(self, obj: Object, entity_type: Enum, override: bool = True):
        "Create the layer if needed and returns its name. Depends on the type of obj passed as parameter"
        exp = self.exporter
        layer_settings = exp.settings.get_entity_settings(
            entity_type).layer_settings
        layer_to = layer_settings.entity_layer_to
        suffix = exp.settings.data_settings.get_sub_layer_suffix(entity_type)
        if layer_to == EntityLayer.COLLECTION.value:
            return self.get_or_create_layer_from_collection(obj.users_collection[0], suffix, override)
        elif layer_to == EntityLayer.DATA_NAME.value:
            return obj.data.name + suffix
        elif layer_to == EntityLayer.OBJECT_NAME.value:
            return self.get_or_create_layer_from_object(obj, suffix, override, layer_settings)
        elif layer_to == EntityLayer.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return self.get_or_create_layer_from_material(obj.data.materials[0], suffix=suffix, layer_settings=layer_settings)
        elif layer_to == EntityLayer.SCENE_NAME.value:
            return exp.context.scene.name + suffix
        return '0' + suffix
