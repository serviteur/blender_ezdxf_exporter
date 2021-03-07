import bmesh
from bpy.types import (
    Object,
    Collection,
    Material,
)
from .shared_properties import (
    entity_color,
    dxf_mesh_type,
    entity_layer,
    get_256_rgb_a,
)


def get_layer_name(layers, context, obj, layer):
    if layer == entity_layer.COLLECTION.value:
        coll = obj.users_collection[0]
        if coll.name not in layers:
            new_layer = layers.new(coll.name)
            new_layer.rgb, _ = MSPInterfaceColor._get_collection_color(coll, context)
        return coll.name
    elif layer == entity_layer.COLLECTION.DATA_NAME.value:
        return obj.data.name
    elif layer == entity_layer.COLLECTION.OBJECT_NAME.value:
        if obj.name not in layers:
            new_layer = layers.new(obj.name)
            rgb, a = MSPInterfaceColor._get_object_color(obj)
            new_layer.rgb, new_layer.transparency = rgb, 1 - a
        return obj.name
    elif layer == entity_layer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
        mat = obj.data.materials[0]
        if mat.name not in layers:
            new_layer = layers.new(mat.name)
            rgb, a = MSPInterfaceColor._get_material_color(mat)
            new_layer.rgb, new_layer.transparency = rgb, 1 - a
        return mat.name
    elif layer == entity_layer.SCENE_NAME.value:
        return context.scene.name
    return '0'

class MSPInterfaceColor:
    @staticmethod
    def get_ACI_color(color):
        if color == entity_color.BYLAYER.value:
            return 256
        elif color == entity_color.BYBLOCK.value:
            return 0
        return 257

    @staticmethod
    def get_color(context, obj, color):
        if color == entity_color.COLLECTION.value:
            return MSPInterfaceColor._get_collection_color(obj.users_collection[0], context)
        elif color == entity_color.OBJECT.value:
            return MSPInterfaceColor._get_object_color(obj)
        elif color == entity_color.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return MSPInterfaceColor._get_material_color(obj.data.materials[0])
        return (0, 0, 0), 1

    @staticmethod
    def _get_collection_color(coll: Collection, context):
        coll_colors = context.preferences.themes[0].collection_color
        if coll_colors is not None:
            color_tag = coll.color_tag
            if color_tag != 'NONE':
                return get_256_rgb_a(coll_colors[int(color_tag[-2:])-1].color)
            else:
                return (0, 0, 0), 1

    @staticmethod
    def _get_object_color(obj: Object):
        return get_256_rgb_a(obj.color)

    @staticmethod
    def _get_material_color(mat: Material):
        return get_256_rgb_a(mat.diffuse_color)


class MSPInterfaceMesh:
    @staticmethod    
    def triangulate_if_needed(mesh, obj_type, mesh_as):
        # Make sure there is no N-Gon (not supported in DXF Faces)
        if obj_type != 'MESH' or mesh_as not in (
                dxf_mesh_type.FACES3D.value, 
                dxf_mesh_type.POLYFACE.value):
            return
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()
    

    @staticmethod
    def create_mesh(mesh_type):
        if mesh_type == dxf_mesh_type.FACES3D.value:
            return MSPInterfaceMesh._create_mesh_3dfaces
        elif mesh_type == dxf_mesh_type.POLYFACE.value:
            return MSPInterfaceMesh._create_mesh_polyface
        elif mesh_type == dxf_mesh_type.POLYLINES.value:
            return MSPInterfaceMesh._create_mesh_polylines
        elif mesh_type == dxf_mesh_type.LINES.value:
            return MSPInterfaceMesh._create_mesh_lines
        elif mesh_type == dxf_mesh_type.POINTS.value:
            return MSPInterfaceMesh._create_mesh_points

    @staticmethod
    def _create_mesh_points(msp, mesh, matrix, dxfattribs):
        for v in mesh.vertices:
            msp.add_point(
                matrix @ v.co,
                dxfattribs=dxfattribs)

    @staticmethod
    def _create_mesh_lines(msp, mesh, matrix, dxfattribs):
        for e in mesh.edges:
            msp.add_line(
                matrix @ mesh.vertices[e.vertices[0]].co,
                matrix @ mesh.vertices[e.vertices[1]].co,
                dxfattribs=dxfattribs)

    @staticmethod
    def _create_mesh_polylines(msp, mesh, matrix, dxfattribs):
        for e in mesh.edges:
            msp.add_polyline3d(
                (
                    matrix @ mesh.vertices[e.vertices[0]].co,
                    matrix @ mesh.vertices[e.vertices[1]].co,
                ),
                dxfattribs=dxfattribs)

    @staticmethod
    def _create_mesh_polyface(msp, mesh, matrix, dxfattribs):
        polyface = msp.add_polyface(dxfattribs=dxfattribs)
        polyface.append_faces(
            [[matrix @ mesh.vertices[v].co for v in f.vertices]
                for f in mesh.polygons],
            dxfattribs=dxfattribs)
        polyface.optimize()

    @staticmethod
    def _create_mesh_3dfaces(msp, mesh, matrix, dxfattribs):
        for f in mesh.polygons:
            msp.add_3dface(
                [matrix @ mesh.vertices[v].co for v in f.vertices],
                dxfattribs=dxfattribs)
