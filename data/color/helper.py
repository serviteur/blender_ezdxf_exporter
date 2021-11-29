from .constants import ACI_RGB_MAPPING, ACIColor, EntityColor


def get_aci_colors(self, context):
    if not hasattr(get_aci_colors, "colors"):
        setattr(get_aci_colors, "colors", [])
    if not get_aci_colors.colors:
        get_aci_colors.colors = [aci.value for aci in ACIColor]
        get_aci_colors.colors.extend(((str(i), str(i), str(ACI_RGB_MAPPING[i])) for i in range(8, 256)))
    return get_aci_colors.colors


def source_has_alpha(source: EntityColor):
    return source in (
        EntityColor.OBJECT.value,
        EntityColor.MATERIAL.value,
        EntityColor.CUSTOM.value,
    )
