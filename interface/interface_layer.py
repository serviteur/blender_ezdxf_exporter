from ..shared_properties import entity_layer
from .interface import Interface


class InterfaceLayer(Interface):
    def create_layer_if_needed_and_get_name(self, obj, suffix=""):
        exp = self.exporter
        layers = exp.doc.layers
        context = exp.context
        layer_to = exp.settings.entity_layer_to
        if layer_to == entity_layer.COLLECTION.value:
            coll = obj.users_collection[0]
            layer_name = coll.name + suffix
            if layer_name not in layers:
                new_layer = layers.new(layer_name)
                rgb, _ = exp.interface_color._get_collection_color(coll)
                if rgb:
                    new_layer.rgb = rgb
            return layer_name
        elif layer_to == entity_layer.COLLECTION.DATA_NAME.value:
            return obj.data.name + suffix
        elif layer_to == entity_layer.COLLECTION.OBJECT_NAME.value:
            layer_name = obj.name + suffix
            if layer_name not in layers:
                new_layer = layers.new()
                rgb, a = exp.interface_color._get_object_color(obj)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == entity_layer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            layer_name = mat.name + suffix
            if layer_name not in layers:
                new_layer = layers.new()
                rgb, a = exp.interface_color._get_material_color(mat)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == entity_layer.SCENE_NAME.value:
            return context.scene.name + suffix
        return '0' + suffix