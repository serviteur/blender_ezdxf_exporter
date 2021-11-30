from ezdxf_exporter.core.export.prop import DataExporter
from .constants import EntityColor
from .helper import (
    get_256_rgb_a,
    rgb_to_hex,
    get_material_color,
    get_object_color,
)


class ColorExporter(DataExporter):
    "Methods for object color access and modification"

    def populate_dxfattribs(self, obj, dxfattribs, entity_type):
        "Sets color properties of the internal dictionary according to object properties"
        color_settings = self.exporter.settings.get_entity_settings(entity_type).color
        dxfattribs["color"] = self.get_ACI_color(color_settings)  # Set Bylayer, Byblock, or other color on entity
        obj_color, obj_alpha = self.get_color(obj, color_settings)
        if (obj_alpha or obj_alpha == 0) and color_settings.entity_color_use_transparency:
            dxfattribs["transparency"] = 1 - obj_alpha
        if obj_color and dxfattribs["color"] == 257:  # 257 is True Color
            dxfattribs["true_color"] = int(rgb_to_hex(obj_color, 256), 16)
        return True

    def get_ACI_color(self, color_settings):
        "Returns the color as Autocad Color Index"
        if color_settings.entity_color_to == EntityColor.BYLAYER.value:
            return 256
        elif color_settings.entity_color_to == EntityColor.BYBLOCK.value:
            return 0
        elif color_settings.entity_color_to == EntityColor.ACI.value:
            return int(color_settings.entity_color_aci)
        return 257

    def get_color(self, obj, color_settings):
        "Return the relevant color information. Depends on the type of object passed as parameter"
        if color_settings.entity_color_to == EntityColor.COLLECTION.value:
            return self._get_collection_color(obj.users_collection[0])
        elif color_settings.entity_color_to == EntityColor.OBJECT.value:
            return get_object_color(obj)
        elif color_settings.entity_color_to == EntityColor.CUSTOM.value:
            return get_256_rgb_a(color_settings.entity_color_custom)
        elif (
            color_settings.entity_color_to == EntityColor.MATERIAL.value
            and obj.data.materials
            and obj.data.materials[0] is not None
        ):
            return get_material_color(obj.data.materials[0])
        return None, None

    def get_color_from_custom_prop(self, obj, prop_name):
        prop = obj.get(prop_name)
        if isinstance(prop, str):
            return
        elif isinstance(prop, (int, float)):  # ACI color
            return max(0, min(255, int(prop)))
        elif len(prop) > 2:            
            if len(prop) == 3:
                prop = [prop[0], prop[1], prop[2], 1 if isinstance(prop[0], float) else 255]
            if isinstance(prop[0], float):
                prop = [min(255, int(c * 255)) for c in prop[0:3]] + [prop[3]]
            else:
                prop = [c for c in prop[0:3]] + [prop[3] / 255] 
            return prop

    def _get_collection_color(self, coll):
        "Returns the color tag of collection or of first parent that has one if setting is selected"
        exp = self.exporter
        coll_colors = exp.context.preferences.themes[0].collection_color
        if coll_colors is not None:
            color_tag = coll.color_tag
            if color_tag != "NONE":
                return get_256_rgb_a(coll_colors[int(color_tag[-2:]) - 1].color)
            elif exp.coll_parents is not None:
                parent = exp.coll_parents.get(coll)
                while parent is not None:
                    if parent.color_tag != "NONE":
                        return get_256_rgb_a(coll_colors[int(parent.color_tag[-2:]) - 1].color)
                    parent = exp.coll_parents.get(parent)
        return None, None
