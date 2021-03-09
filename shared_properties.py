from enum import Enum
import struct


class dxf_face_type(Enum):
    NONE = "Don't Export"
    MESH = "MESH"
    FACES3D = "3DFACEs"
    POLYFACE = 'POLYFACE'


class dxf_line_type(Enum):
    NONE = "Don't Export"
    LINES = 'LINEs'
    POLYLINES = 'POLYLINEs'


class dxf_point_type(Enum):
    NONE = "Don't Export"    
    POINTS = 'POINTs'


class entity_layer(Enum):
    NONE = 'Default'
    COLLECTION = 'Collection'
    OBJECT_NAME = 'Object Name'
    DATA_NAME = 'Mesh Name'
    SCENE_NAME = 'Scene Name'
    MATERIAL = 'Material'


class entity_color(Enum):
    BYLAYER= 'BYLAYER'
    BYBLOCK = 'BYBLOCK'
    OBJECT = 'Object Color'
    MATERIAL = 'Material Color'
    COLLECTION = 'Collection Tag Color'   


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
