from ..shared_properties import entity_color
from ..shared_maths import get_256_rgb_a
from .interface import Interface


class InterfaceColor(Interface):
    def get_ACI_color(self):
        exp = self.exporter
        if exp.settings.entity_color_to == entity_color.BYLAYER.value:
            return 256
        elif exp.settings.entity_color_to == entity_color.BYBLOCK.value:
            return 0
        return 257

    def get_color(self, obj):
        settings = self.exporter.settings
        if settings.entity_color_to == entity_color.COLLECTION.value:
            return self._get_collection_color(obj.users_collection[0])
        elif settings.entity_color_to == entity_color.OBJECT.value:
            return self._get_object_color(obj)
        elif settings.entity_color_to == entity_color.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return self._get_material_color(obj.data.materials[0])
        return False, False

    def _get_collection_color(self, coll):
        exp = self.exporter
        coll_colors = exp.context.preferences.themes[0].collection_color
        if coll_colors is not None:
            color_tag = coll.color_tag
            if color_tag != 'NONE':
                return get_256_rgb_a(coll_colors[int(color_tag[-2:])-1].color)
            elif exp.coll_parents is not None:
                parent = exp.coll_parents.get(coll)
                while parent is not None:
                    if parent.color_tag != 'NONE':
                        return get_256_rgb_a(coll_colors[int(parent.color_tag[-2:])-1].color)
                    parent = exp.coll_parents.get(parent)
        return False, False

    @classmethod
    def _get_object_color(cls, obj):
        return get_256_rgb_a(obj.color)

    @classmethod
    def _get_material_color(cls, mat):
        return get_256_rgb_a(mat.diffuse_color)
