from ..shared_properties import entity_layer
from .manager import Manager


class LayerManager(Manager):
    def populate_dxfattribs(self, obj, dxfattribs, suffix="", override=True):
        dxfattribs['layer'] = self.get_or_create_layer(obj, suffix, override)

    def get_or_create_layer(self, obj, suffix="", override=True):
        "Create the layer if needed and returns its name. Depends on the type of obj passed as parameter"
        exp = self.exporter
        layers = exp.doc.layers
        context = exp.context
        layer_to = exp.settings.layer_settings.entity_layer_to
        if layer_to == entity_layer.COLLECTION.value:
            coll = obj.users_collection[0]
            layer_name = coll.name + suffix
            if override and layer_name not in layers:
                new_layer = layers.new(layer_name)
                rgb, _ = exp.color_mgr._get_collection_color(coll)
                if rgb:
                    new_layer.rgb = rgb
            return layer_name
        elif layer_to == entity_layer.COLLECTION.DATA_NAME.value:
            return obj.data.name + suffix
        elif layer_to == entity_layer.COLLECTION.OBJECT_NAME.value:
            layer_name = obj.name + suffix
            if override and layer_name not in layers:
                new_layer = layers.new()
                rgb, a = exp.color_mgr._get_object_color(obj)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.layer_settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == entity_layer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            layer_name = mat.name + suffix
            if override and layer_name not in layers:
                new_layer = layers.new()
                rgb, a = exp.color_mgr._get_material_color(mat)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.layer_settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == entity_layer.SCENE_NAME.value:
            return context.scene.name + suffix
        return '0' + suffix