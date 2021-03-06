import ezdxf
import bpy


class DXFExporter:
    def __init__(self):
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()

    def create_layers(self, context):
        collection_colors = context.preferences.themes[0].collection_color
        for coll in bpy.data.collections:
            new_layer = self.doc.layers.new(coll.name)

            color_tag = coll.color_tag
            if color_tag != 'NONE':
                col = [int(channel * 256)
                    for channel in collection_colors[int(color_tag[-2:])-1].color]
                new_layer.rgb = col

    def write_objects(self, objects):
        [self.write_object(obj) for obj in objects]

    def write_object(self, obj):
        mesh = obj.data

        obj_matrix_world = obj.matrix_world

        for e in mesh.edges:
            self.msp.add_line(
                obj_matrix_world @ mesh.vertices[e.vertices[0]].co,
                obj_matrix_world @ mesh.vertices[e.vertices[1]].co,
                dxfattribs={
                    'layer': obj.users_collection[0].name
                })
    
        # Add entities to a layout by factory methods: layout.add_...()
        # msp.add_text(
        #    'Test',
        #    dxfattribs={
        #        'layer': 'TEXTLAYER'
        #    }).set_pos((0, 0.2), align='CENTER')

    def export_file(self, path):
        self.doc.saveas(path)
