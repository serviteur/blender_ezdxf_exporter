import math
import struct

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy, _ = origin
    px, py, _ = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy, 0


def get_256_rgb_a(color):
    rgb = [int(channel * 255) for channel in color[0:3]]
    if len(color) > 3:
        return rgb, color[3]
    else:
        return rgb, 1


def rgb_to_hex(vals, rgbtype=1):
  """Converts RGB values in a variety of formats to Hex values.

     @param  vals     An RGB/RGBA tuple
     @param  rgbtype  Valid valus are:
                          1 - Inputs are in the range 0 to 1
                        256 - Inputs are in the range 0 to 255

     @return A hex string in the form '0xRRGGBB' or '0xRRGGBBAA'
"""

  if len(vals)!=3 and len(vals)!=4:
    raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
  if rgbtype!=1 and rgbtype!=256:
    raise Exception("rgbtype must be 1 or 256!")

  #Convert from 0-1 RGB/RGBA to 0-255 RGB/RGBA
  if rgbtype==1:
    vals = [255*x for x in vals]

  #Ensure values are rounded integers, convert to hex, and concatenate
  return '0x' + ''.join(['{:02X}'.format(int(round(x))) for x in vals])


def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])
