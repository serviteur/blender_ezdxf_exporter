mesh_as_items = (
    ('NO', 'Do not export', ''),
    ('3DFACEs', '3DFACEs', ''),
    ('POLYFACE', 'POLYFACE', ''),
    ('POLYLINE', 'POLYLINE', ''),
    ('LINEs', 'LINEs', 'export Mesh as multiple LINEs'),
    ('POINTs', 'POINTs', 'Export Mesh as multiple POINTs')
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