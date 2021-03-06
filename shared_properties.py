from enum import Enum

class dxf_mesh_type(Enum):
    NONE = 'Do not export'
    FACES3D = '3DFACEs'
    POLYFACE = 'POLYFACE'
    POLYLINES = 'POLYLINEs'
    LINES = 'LINEs'
    POINTS = 'POINTs'

class entity_layer(Enum):
    NONE = 'Default'
    COLLECTION = 'Collection'
    OBJECT_NAME = 'Object Name'
    DATA_NAME = 'Mesh Name'
    MATERIAL = 'Material'
