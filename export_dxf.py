import ezdxf
import bmesh
import bpy
from .shared_properties import (
    dxf_mesh_type,
    entity_layer,
    entity_color,
    get_256_rgb_a,
    rgb_to_hex,
    float_to_hex,
)
from .modelspace import (
    MSPInterfaceMesh,
)


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
            color
            ):
        [self.write_object(
            obj=obj,
            context=context,
            mesh_as=mesh_as,
            layer=layer,
            color=color,
        )
            for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")

    def get_collection_color(self, coll: bpy.types.Collection, context):
        coll_colors = context.preferences.themes[0].collection_color
        if coll_colors is not None:
            color_tag = coll.color_tag
            if color_tag != 'NONE':
                return get_256_rgb_a(coll_colors[int(color_tag[-2:])-1].color)
            else:
                return (0, 0, 0), 1

    def get_object_color(self, obj: bpy.types.Object):
        return get_256_rgb_a(obj.color)

    def get_material_color(self, mat: bpy.types.Material):
        return get_256_rgb_a(mat.diffuse_color)

    def get_layer_name(self, context, obj, layer) -> str:
        if layer == entity_layer.COLLECTION.value:
            coll = obj.users_collection[0]
            if coll.name not in self.doc.layers:
                new_layer = self.doc.layers.new(coll.name)
                new_layer.rgb, _ = self.get_collection_color(coll, context)
            return coll.name
        elif layer == entity_layer.COLLECTION.DATA_NAME.value:
            return obj.data.name
        elif layer == entity_layer.COLLECTION.OBJECT_NAME.value:
            if obj.name not in self.doc.layers:
                new_layer = self.doc.layers.new(obj.name)
                rgb, a = self.get_object_color(obj)
                new_layer.rgb, new_layer.transparency = rgb, 1 - a
            return obj.name
        elif layer == entity_layer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            mat = obj.data.materials[0]
            if mat.name not in self.doc.layers:
                new_layer = self.doc.layers.new(mat.name)
                rgb, a = self.get_material_color(mat)
                new_layer.rgb, new_layer.transparency = rgb, 1 - a
            return mat.name
        elif layer == entity_layer.SCENE_NAME.value:
            return context.scene.name
        return '0'
    
    def get_color_by(self, color):
        if color == entity_color.BYLAYER.value:
            return 256
        elif color == entity_color.BYBLOCK.value:
            return 0
        return 257    
    
    def get_color(self, context, obj, color):
        if color == entity_color.COLLECTION.value:
            return self.get_collection_color(obj.users_collection[0])
        elif color == entity_color.OBJECT.value:
            return self.get_object_color(obj)
        elif color == entity_color.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return self.get_material_color(obj.data.materials[0])
        return (0, 0, 0), 1
        

    def is_object_supported(self, obj):
        if obj.type in self.supported_types:
            return True
        else:
            if self.debug_mode:
                self.log.append(
                    f"{obj.name} NOT exported : Couldn't be converted to a mesh.")
                self.not_exported_objects += 1
            return False

    def write_object(
            self,
            obj,
            context,
            mesh_as,
            layer='0',
            color='BYLAYER'
            ):

        if not self.is_object_supported(obj):
            return

        depsgraph = context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)

        dxfattribs = {
            'layer': self.get_layer_name(context, obj, layer),
            'color': self.get_color_by(color)
        }

        obj_color, obj_alpha = self.get_color(context, obj, color)
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

        MSPInterfaceMesh.triangulate_if_needed(mesh, obj.type, mesh_as)

        # Support for multiple mesh export type later on in development.
        # For example, user wants to export Points AND Faces
        for mesh_creation_method in [MSPInterfaceMesh.create_mesh(mesh_as), ]:
            if mesh_creation_method is None:
                continue
            mesh_creation_method(self.msp, mesh, obj_matrix_world, dxfattribs)

    def export_file(self, path):
        self.doc.entitydb.purge()
        self.doc.saveas(path)
