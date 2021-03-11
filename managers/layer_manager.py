from ..settings.layer_settings import EntityLayer
from .manager import Manager


class LayerManager(Manager):
    def populate_dxfattribs(self, obj, dxfattribs, entity_type, override=True):
        dxfattribs['layer'] = self.get_or_create_layer(obj, entity_type, override)

    def get_or_create_layer_from_material(self, mat):
        if mat is None:
            return
        exp = self.exporter
        layers = exp.doc.layers
        layer_name = "MATERIAL_" + mat.name
        if layer_name not in layers:
            new_layer = layers.new(layer_name)
            rgb, a = exp.color_mgr._get_material_color(mat)
            new_layer.rgb, new_layer.transparency = rgb, 1 - \
                a if exp.settings.layer_settings.entity_layer_transparency else 0
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
            if override and layer_name not in layers:
                new_layer = layers.new(layer_name)
                rgb, _ = exp.color_mgr._get_collection_color(coll)
                if rgb:
                    new_layer.rgb = rgb
            return layer_name
        elif layer_to == EntityLayer.COLLECTION.DATA_NAME.value:
            return obj.data.name + suffix
        elif layer_to == EntityLayer.COLLECTION.OBJECT_NAME.value:
            layer_name = obj.name + suffix
            if override and layer_name not in layers:
                new_layer = layers.new(layer_name)
                rgb, a = exp.color_mgr._get_object_color(obj)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.layer_settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == EntityLayer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            layer_name = mat.name + suffix
            if override and layer_name not in layers:
                new_layer = layers.new(layer_name)
                rgb, a = exp.color_mgr._get_material_color(mat)
                new_layer.rgb, new_layer.transparency = rgb, 1 - \
                    a if exp.settings.layer_settings.entity_layer_transparency else 0
            return layer_name
        elif layer_to == EntityLayer.SCENE_NAME.value:
            return context.scene.name + suffix
        return '0' + suffix