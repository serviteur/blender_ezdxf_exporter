from ..settings.layer_settings import (
    EntityLayer,
    ExcludedObject,
)
from .manager import Manager


class LayerManager(Manager):
    def populate_dxfattribs(self, obj, dxfattribs, entity_type, override=True):
        "Populates the 'Layer' key of dxfattribs dict, returns False if no layer should be created"
        dxfattribs['layer'] = self.get_or_create_layer(
            obj, entity_type, override)
        return dxfattribs['layer'] is not None

    def create_layer(self, name, rgb=None, transparency=None, freeze=False):
        layer = self.exporter.doc.layers.new(name)
        if rgb is not None:
            layer.rgb = rgb
        if transparency is not None:
            layer.transparency = transparency
        if freeze:
            layer.freeze()
        return layer

    def get_or_create_layer_from_material(self, mat):
        if mat is None:
            return
        exp = self.exporter
        layers = exp.doc.layers
        layer_name = "MATERIAL_" + mat.name
        if layer_name not in layers:
            rgb, a = exp.color_mgr._get_material_color(mat)
            self.create_layer(
                layer_name,
                rgb,
                1 - a if exp.settings.layer_settings.entity_layer_transparency else 0)
        return layer_name

    def get_or_create_layer(self, obj, entity_type, override=True):
        "Create the layer if needed and returns its name. Depends on the type of obj passed as parameter"
        exp = self.exporter
        layers = exp.doc.layers
        context = exp.context
        layer_to = exp.settings.layer_settings.entity_layer_to
        suffix = exp.settings.data_settings.get_sub_layer_suffix(entity_type)
        if layer_to == EntityLayer.COLLECTION.value:
            coll = obj.users_collection[0]
            layer_name = coll.name + suffix
            excluded_from_view_layer = context.view_layer.layer_collection.children[coll.name].exclude
            col_exclude_state = exp.settings.layer_settings.layer_excluded_export
            if excluded_from_view_layer and col_exclude_state == ExcludedObject.NONE.value:
                return None
            if override and layer_name not in layers:
                self.create_layer(
                    layer_name,
                    rgb=exp.color_mgr._get_collection_color(coll)[0],
                    freeze=col_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer)
            return layer_name
        elif layer_to == EntityLayer.DATA_NAME.value:
            return obj.data.name + suffix
        elif layer_to == EntityLayer.OBJECT_NAME.value:
            layer_name = obj.name + suffix            
            excluded_from_view_layer = obj.hide_get() or obj.hide_viewport
            obj_exclude_state = exp.settings.layer_settings.layer_excluded_export
            if excluded_from_view_layer and obj_exclude_state == ExcludedObject.NONE.value:
                return None
            if override and layer_name not in layers:
                rgb, a = exp.color_mgr._get_object_color(obj)
                self.create_layer(
                    layer_name,
                    rgb=rgb,
                    transparency=1 - a if exp.settings.layer_settings.entity_layer_transparency else 0,
                    freeze=obj_exclude_state == ExcludedObject.FROZEN.value and excluded_from_view_layer)
            return layer_name
        elif layer_to == EntityLayer.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            layer_name = mat.name + suffix
            if override and layer_name not in layers:
                rgb, a = exp.color_mgr._get_material_color(mat)
                self.create_layer(
                    layer_name,
                    rgb=rgb,
                    transparency=1 - a if exp.settings.layer_settings.entity_layer_transparency else 0)
            return layer_name
        elif layer_to == EntityLayer.SCENE_NAME.value:
            return context.scene.name + suffix
        return '0' + suffix
