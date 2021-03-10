from ..shared_properties import entity_color
from ..shared_maths import get_256_rgb_a
from .interface import Interface


class InterfaceColor(Interface):
    "Methods for object color access and modification"

    def get_ACI_color(self):
        "Returns the color as Autocad Color Index"
        exp = self.exporter
        if exp.settings.entity_color_to == entity_color.BYLAYER.value:
            return 256
        elif exp.settings.entity_color_to == entity_color.BYBLOCK.value:
            return 0
        return 257

    def get_color(self, obj):
        "Return the relevant color information. Depends on the type of object passed as parameter"
        settings = self.exporter.settings
        if settings.entity_color_to == entity_color.COLLECTION.value:
            return self._get_collection_color(obj.users_collection[0])
        elif settings.entity_color_to == entity_color.OBJECT.value:
            return self._get_object_color(obj)
        elif settings.entity_color_to == entity_color.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return self._get_material_color(obj.data.materials[0])
        return False, False

    def _get_collection_color(self, coll):
        "Returns the color tag of collection or of first parent that has one if setting is selected"
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
        "Returns the object color as a 0-255 rgb color"
        return get_256_rgb_a(obj.color)

    @classmethod
    def _get_material_color(cls, mat):
        "Returns the material color as a 0-255 rgb color"
        return get_256_rgb_a(mat.diffuse_color)
