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
    BYLAYER= 'BYLAYER'
    BYBLOCK = 'BYBLOCK'
    OBJECT = 'Object Color'
    MATERIAL = 'Material Color'
    COLLECTION = 'Collection Tag Color'   
    # TODO : Custom property ?
