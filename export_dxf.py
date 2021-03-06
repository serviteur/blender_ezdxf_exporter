import ezdxf
import bpy


class DXFExporter:
    def __init__(self, debug_mode=False):
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self.debug_mode = debug_mode
        self.log = []
        self.exported_objects = 0
        self.not_exported_objects = 0

    def create_layers(self, context):
        collection_colors = context.preferences.themes[0].collection_color
        for coll in bpy.data.collections:
            new_layer = self.doc.layers.new(coll.name)

            color_tag = coll.color_tag
            if color_tag != 'NONE':
                col = [int(channel * 256)
                    for channel in collection_colors[int(color_tag[-2:])-1].color]
                new_layer.rgb = col

    def write_objects(
            self, 
            objects, 
            context, 
            apply_modifiers=True):
        [self.write_object(
            obj, 
            context, 
            apply_modifiers) 
            for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(f"NOT Exported : {self.not_exported_objects} Objects")

    def write_object(
            self, 
            obj, 
            context, 
            apply_modifiers=True):
        collection = obj.users_collection[0]
        supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

        if obj.type not in supported_types:
            if self.debug_mode:
                self.log.append(f"{obj.name} NOT exported : Couldn't be converted to a mesh.")
                self.not_exported_objects += 1
            return

        if apply_modifiers or obj.type == 'META':
            depsgraph = context.evaluated_depsgraph_get()
            obj = obj.evaluated_get(depsgraph)

        obj_matrix_world = obj.matrix_world
        
        mesh = obj.to_mesh()

        for e in mesh.edges:
            self.msp.add_line(
                obj_matrix_world @ mesh.vertices[e.vertices[0]].co,
                obj_matrix_world @ mesh.vertices[e.vertices[1]].co,
                dxfattribs={
                    'layer': collection.name
                })
        
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1
    
        # Add entities to a layout by factory methods: layout.add_...()
        # msp.add_text(
        #    'Test',
        #    dxfattribs={
        #        'layer': 'TEXTLAYER'
        #    }).set_pos((0, 0.2), align='CENTER')

    def export_file(self, path):
        self.doc.saveas(path)
