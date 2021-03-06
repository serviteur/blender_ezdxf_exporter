import ezdxf
import bpy
from .shared_properties import mesh_types


class DXFExporter:
    supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

    def __init__(self, debug_mode=False):
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self.debug_mode = debug_mode
        self.log = []
        self.exported_objects = 0
        self.not_exported_objects = 0

    def write_objects(
            self,
            objects,
            context,
            mesh_as,
            layer,
            apply_modifiers=True):
        [self.write_object(
            obj=obj,
            context=context,
            apply_modifiers=apply_modifiers,
            mesh_as=mesh_as,
            layer=layer,
        )
            for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")

    def get_collection_layer_name(self, coll: bpy.types.Collection, coll_colors=None) -> str:         
        if coll.name not in self.doc.layers:                
            new_layer = self.doc.layers.new(coll.name)
            
            if coll_colors is not None:
                color_tag = coll.color_tag
                if color_tag != 'NONE':
                    col = [int(channel * 256)
                        for channel in coll_colors[int(color_tag[-2:])-1].color]
                    new_layer.rgb = col
        
        return coll.name

    def get_layer_name(self, coll_colors, obj, layer) -> str:
        if layer == 'collection':            
            return self.get_collection_layer_name(obj.users_collection[0], coll_colors)
        elif layer == 'data':
            return obj.data.name
        elif layer == 'name':
            return obj.name
        elif layer == 'material' and obj.data.materials:
            return obj.data.materials[0].name
        return '0'
    
    def is_object_supported(self, obj):
        if obj.type in self.supported_types:
            return True
        else:
            if self.debug_mode:
                self.log.append(
                    f"{obj.name} NOT exported : Couldn't be converted to a mesh.")
                self.not_exported_objects += 1
            return False
    
    def get_export_obj(self, obj, apply_modifiers, context):
        if apply_modifiers or obj.type == 'META':
            depsgraph = context.evaluated_depsgraph_get()
            return obj.evaluated_get(depsgraph)
        else:
            return obj

    def write_object(
            self,
            obj,
            context,
            mesh_as,
            layer='0',
            apply_modifiers=True):

        if not self.is_object_supported(obj):
            return

        export_obj = self.get_export_obj(apply_modifiers, context)

        coll_colors = context.preferences.themes[0].collection_color
        dxfattribs = {
            'layer': self.get_layer_name(coll_colors, obj, layer)
        }

        self.export_mesh(export_obj, dxfattribs, mesh_as)
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def export_mesh(self, obj, dxfattribs, mesh_as):    
        obj_matrix_world = obj.matrix_world
        mesh = obj.to_mesh()   
        # Support for multiple mesh export type later on in development.
        # For example, user wants to export Points AND Faces
        mesh_creation_methods = []

        if mesh_as == mesh_types.FACES3D:  # 3D Faces
            mesh_creation_methods.append(self.create_mesh_3dfaces)
        if mesh_as == mesh_types.POLYFACE:  # Polyfaces
            mesh_creation_methods.append(self.create_mesh_polyface)
        if mesh_as == mesh_types.POLYLINES:  # Polylines
            mesh_creation_methods.append(self.create_mesh_polylines)
        if mesh_as == mesh_types.POLYLINES:  # Lines
            mesh_creation_methods.append(self.create_mesh_lines)
        elif mesh_as == mesh_types.POINTS:  # Points
            mesh_creation_methods.append(self.create_mesh_points)
        
        for mesh_creation_method in mesh_creation_methods:
            mesh_creation_method(mesh, obj_matrix_world, dxfattribs)

    def create_mesh_points(self, mesh, matrix, dxfattribs):
        for v in mesh.vertices:
            self.msp.add_point(
                matrix @ v.co,
                dxfattribs=dxfattribs)

    def create_mesh_lines(self, mesh, matrix, dxfattribs):
        for e in mesh.edges:
            self.msp.add_line(
                matrix @ mesh.vertices[e.vertices[0]].co,
                matrix @ mesh.vertices[e.vertices[1]].co,
                dxfattribs=dxfattribs)

    def create_mesh_polylines(self, mesh, matrix, dxfattribs):
        for e in mesh.edges:
            self.msp.add_polyline3d(
                (
                    matrix @ mesh.vertices[e.vertices[0]].co,
                    matrix @ mesh.vertices[e.vertices[1]].co,
                ),
                dxfattribs=dxfattribs)

    def create_mesh_polyface(self, mesh, matrix, dxfattribs):        
        polyface = self.msp.add_polyface(dxfattribs=dxfattribs)
        polyface.append_faces(
            [[matrix @ mesh.vertices[v].co for v in f.vertices] for f in mesh.polygons],
            dxfattribs=dxfattribs)
        polyface.optimize()

    def create_mesh_3dfaces(self, mesh, matrix, dxfattribs):           
        for f in mesh.polygons:
            self.msp.add_3dface(
                [matrix @ mesh.vertices[v].co for v in f.vertices],
                dxfattribs=dxfattribs)

    def export_file(self, path):
        self.doc.entitydb.purge()
        self.doc.saveas(path)
