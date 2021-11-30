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


def get_256_rgb_a(color):
    rgb = [int(channel * 255) for channel in color[0:3]]
    if len(color) > 3:
        return rgb, (color[3] * 255)
    else:
        return rgb, 1


def rgb_to_hex(vals, rgbtype=1):
    """Converts RGB values in a variety of formats to Hex values.

    @param  vals     An RGB/RGBA tuple
    @param  rgbtype  Valid valus are:
                         1 - Inputs are in the range 0 to 1
                       256 - Inputs are in the range 0 to 255

    @return A hex string in the form '0xRRGGBB' or '0xRRGGBBAA'"""

    if len(vals) != 3 and len(vals) != 4:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
    if rgbtype != 1 and rgbtype != 256:
        raise Exception("rgbtype must be 1 or 256!")

    # Convert from 0-1 RGB/RGBA to 0-255 RGB/RGBA
    if rgbtype == 1:
        vals = [255 * x for x in vals]

    # Ensure values are rounded integers, convert to hex, and concatenate
    return "0x" + "".join(["{:02X}".format(int(round(x))) for x in vals])


def get_object_color(obj):
    "Returns the object color as a 0-255 rgb color + alpha"
    return get_256_rgb_a(obj.color)


def get_material_color(mat):
    "Returns the material color as a 0-255 rgb color + alpha"
    return get_256_rgb_a(mat.diffuse_color)
