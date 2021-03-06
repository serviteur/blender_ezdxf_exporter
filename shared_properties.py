from enum import Enum

class mesh_types(Enum):
    NONE = 'NONE'
    FACES3D = '3DFACES'
    POLYFACE = 'POLYFACE'
    POLYLINES = 'POLYLINES'
    LINES = 'LINES'
    POINTS = 'POINTS'

mesh_as_items = (
    (str(mesh_types.NONE), 'Do not export', ''),
    (str(mesh_types.FACES3D), '3DFACEs', ''),
    (str(mesh_types.POLYFACE), 'POLYFACE', ''),
    (str(mesh_types.POLYLINES), 'POLYLINE', ''),
    (str(mesh_types.LINES), 'LINEs', 'export Mesh as multiple LINEs'),
    (str(mesh_types.POINTS), 'POINTs', 'Export Mesh as multiple POINTs')
)

entity_layer_from_items = (
        ('0', 'Default', ''),
        ('collection', 'Collection', ''),
        ('name', 'Object Name', ''),
        ('data', 'Mesh Name', ''),
        ('material', 'Material', 'Export object as the name of its first material, or in layer 0 if there is None'),
        # ('..vertexgroup', 'Vertex Group', ''),
        # ('..group', 'Group', ''),
        # ('..map_table', 'Table', '')
    )