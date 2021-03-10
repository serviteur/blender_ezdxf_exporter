from enum import Enum


class dxf_face_type(Enum):
    NONE = 'No Export'
    MESH = 'MESH'
    FACES3D = '3DFACEs'
    POLYFACE = 'POLYFACE'


class dxf_line_type(Enum):
    NONE = 'No Export'
    LINES = 'LINEs'
    POLYLINES = 'POLYLINEs'


class dxf_point_type(Enum):
    NONE = 'No Export'
    POINTS = 'POINTs'


class entity_layer(Enum):
    NONE = 'Default (Layer 0)'
    COLLECTION = 'Collection'
    OBJECT_NAME = 'Object Name'
    DATA_NAME = 'Mesh Name'
    SCENE_NAME = 'Current Scene Name'
    MATERIAL = 'Current Material'


class entity_color(Enum):
    BYLAYER = 'BYLAYER'
    BYBLOCK = 'BYBLOCK'
    OBJECT = 'Object Color'
    MATERIAL = 'Material Color'
    COLLECTION = 'Collection Tag Color'
    ACI = 'Autocad Color Index (ACI)'
    # TODO : Custom property ?


def source_has_alpha(source: entity_color):
    return source in (
        entity_color.OBJECT.value,
        entity_color.MATERIAL.value)


class ACI_Colors(Enum):
    WHITE = ("7", "White", "Default Value (7)")
    BLACK = ("0", "Black", "0")
    RED = ("1", "Red", "1")
    YELLOW = ("2", "Yellow", "2")
    GREEN = ("3", "Green", "3")
    CYAN = ("4", "Cyan", "4")
    BLUE = ("5", "Blue", "5")
    MAGENTA = ("6", "Magenta", "6")
