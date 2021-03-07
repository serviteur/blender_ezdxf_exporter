import ezdxf
import bmesh
import bpy
from .shared_properties import (
    entity_layer,
    get_256_rgb_a,
    rgb_to_hex,
    float_to_hex,
)
from .modelspace import create_mesh


class DXFExporter:
    supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

    def __init__(self, debug_mode=False):
        self.doc = ezdxf.new(dxfversion="R2010")  # Create new document
        self.msp = self.doc.modelspace()  # Access to dxf Modelspace
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
        if layer == entity_layer.COLLECTION.value:            
            return self.get_collection_layer_name(obj.users_collection[0], coll_colors)
        elif layer == entity_layer.COLLECTION.DATA_NAME:
            return obj.data.name
        elif layer == entity_layer.COLLECTION.OBJECT_NAME:
            return obj.name
        elif layer == entity_layer.COLLECTION.MATERIAL and obj.data.materials:
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

        export_obj = self.get_export_obj(obj, apply_modifiers, context)

        coll_colors = context.preferences.themes[0].collection_color
        dxfattribs = {
            'layer': self.get_layer_name(coll_colors, obj, layer)
        }

        dxfattribs['transparency'] = int(float_to_hex(1 - obj_alpha), 16)
        dxfattribs['transparency'] = 50
        if dxfattribs['color'] == 257:
            dxfattribs['true_color'] = int(rgb_to_hex(obj_color, 256), 16)

        self.export_mesh(export_obj, dxfattribs, mesh_as)
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def export_mesh(self, obj, dxfattribs, mesh_as):    
        obj_matrix_world = obj.matrix_world
        mesh = obj.to_mesh()

        # Make sure there is no N-Gon (not supported in DXF Faces)
        if obj.type == 'MESH' and mesh_as in (
                dxf_mesh_type.FACES3D.value, 
                dxf_mesh_type.POLYFACE.value):
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh)
            bm.free()

        # Support for multiple mesh export type later on in development.
        # For example, user wants to export Points AND Faces
        for mesh_creation_method in [create_mesh(mesh_as), ]:
            if mesh_creation_method is None:
                continue
            mesh_creation_method(self.msp, mesh, obj_matrix_world, dxfattribs)

    def export_file(self, path):
        self.doc.entitydb.purge()
        self.doc.saveas(path)
