import ezdxf
import bpy
from .shared_properties import mesh_as_items


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
            mesh_as,
            apply_modifiers=True):
        [self.write_object(
            obj=obj,
            context=context,
            apply_modifiers=apply_modifiers,
            mesh_as=mesh_as,
        )
            for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")

    def write_object(
            self,
            obj,
            context,
            mesh_as,
            apply_modifiers=True):
        collection = obj.users_collection[0]
        supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

        if obj.type not in supported_types:
            if self.debug_mode:
                self.log.append(
                    f"{obj.name} NOT exported : Couldn't be converted to a mesh.")
                self.not_exported_objects += 1
            return

        if apply_modifiers or obj.type == 'META':
            depsgraph = context.evaluated_depsgraph_get()
            obj = obj.evaluated_get(depsgraph)

        obj_matrix_world = obj.matrix_world

        mesh = obj.to_mesh()
        dxfattribs = {
            'layer': collection.name
        }
        if mesh_as == mesh_as_items[1][0]:  # 3D Faces            
            for f in mesh.polygons:
                self.msp.add_3dface(
                    [obj_matrix_world @ mesh.vertices[v].co for v in f.vertices],
                    dxfattribs=dxfattribs)
        if mesh_as == mesh_as_items[2][0]:  # Polyfaces
            polyface = self.msp.add_polyface(dxfattribs=dxfattribs)
            polyface.append_faces(
                [[obj_matrix_world @ mesh.vertices[v].co for v in f.vertices] for f in mesh.polygons],
                dxfattribs=dxfattribs)
            polyface.optimize()
        if mesh_as == mesh_as_items[3][0]:  # Polylines
            for e in mesh.edges:
                self.msp.add_polyline3d(
                    (
                        obj_matrix_world @ mesh.vertices[e.vertices[0]].co,
                        obj_matrix_world @ mesh.vertices[e.vertices[1]].co,
                    ),
                    dxfattribs=dxfattribs)
        if mesh_as == mesh_as_items[4][0]:  # Lines
            for e in mesh.edges:
                self.msp.add_line(
                    obj_matrix_world @ mesh.vertices[e.vertices[0]].co,
                    obj_matrix_world @ mesh.vertices[e.vertices[1]].co,
                    dxfattribs=dxfattribs)
        elif mesh_as == mesh_as_items[5][0]:  # Points
            for v in mesh.vertices:
                self.msp.add_point(
                    obj_matrix_world @ v.co,
                    dxfattribs=dxfattribs)

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
