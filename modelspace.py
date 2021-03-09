import ezdxf
import bmesh
from bpy.types import (
    Object,
    Collection,
    Material,
)
from .shared_properties import (
    entity_color,
    dxf_face_type,
    dxf_line_type,
    dxf_point_type,
    entity_layer,
)
from .shared_maths import (
    get_256_rgb_a,
)


def create_layer_if_needed_and_get_name(layers, context, obj, layer, use_transparency, coll_parents=None, suffix=""):
    if layer == entity_layer.COLLECTION.value:
        coll = obj.users_collection[0]
        layer_name = coll.name + suffix
        if layer_name not in layers:
            new_layer = layers.new(layer_name)
            rgb, _ = MSPInterfaceColor._get_collection_color(
                coll, context, coll_parents=coll_parents)
            if rgb:
                new_layer.rgb = rgb
        return layer_name
    elif layer == entity_layer.COLLECTION.DATA_NAME.value:
        return obj.data.name + suffix
    elif layer == entity_layer.COLLECTION.OBJECT_NAME.value:
        layer_name = obj.name + suffix
        if layer_name not in layers:
            new_layer = layers.new()
            rgb, a = MSPInterfaceColor._get_object_color(obj)
            new_layer.rgb, new_layer.transparency = rgb, 1 - a if use_transparency else 0
        return layer_name
    elif layer == entity_layer.COLLECTION.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
        mat = obj.data.materials[0]
        layer_name = mat.name + suffix
        if layer_name not in layers:
            new_layer = layers.new()
            rgb, a = MSPInterfaceColor._get_material_color(mat)
            new_layer.rgb, new_layer.transparency = rgb, 1 - a if use_transparency else 0
        return layer_name
    elif layer == entity_layer.SCENE_NAME.value:
        return context.scene.name + suffix
    return '0' + suffix


class MSPInterfaceColor:
    @staticmethod
    def get_ACI_color(color):
        if color == entity_color.BYLAYER.value:
            return 256
        elif color == entity_color.BYBLOCK.value:
            return 0
        return 257

    @staticmethod
    def get_color(context, obj, color, coll_parents=None):
        if color == entity_color.COLLECTION.value:
            return MSPInterfaceColor._get_collection_color(obj.users_collection[0], context, coll_parents)
        elif color == entity_color.OBJECT.value:
            return MSPInterfaceColor._get_object_color(obj)
        elif color == entity_color.MATERIAL.value and obj.data.materials and obj.data.materials[0] is not None:
            return MSPInterfaceColor._get_material_color(obj.data.materials[0])
        return False, False

    @staticmethod
    def _get_collection_color(coll: Collection, context, coll_parents=None):
        coll_colors = context.preferences.themes[0].collection_color
        if coll_colors is not None:
            color_tag = coll.color_tag
            if color_tag != 'NONE':
                return get_256_rgb_a(coll_colors[int(color_tag[-2:])-1].color)
            elif coll_parents is not None:
                parent = coll_parents.get(coll)
                while parent is not None:
                    if parent.color_tag != 'NONE':
                        return get_256_rgb_a(coll_colors[int(parent.color_tag[-2:])-1].color)
                    parent = coll_parents.get(parent)
        return False, False

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
                dxf_face_type.FACES3D.value,
                dxf_face_type.POLYFACE.value,
                dxf_face_type.MESH.value):
            return
        if any([len(p.vertices) > 4 for p in mesh.polygons]):
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh)
            bm.free()

    @staticmethod
    def create_mesh(mesh_type):
        if mesh_type == dxf_face_type.FACES3D.value:
            return MSPInterfaceMesh._create_mesh_3dfaces
        elif mesh_type == dxf_face_type.MESH.value:
            return MSPInterfaceMesh._create_mesh_mesh
        elif mesh_type == dxf_face_type.POLYFACE.value:
            return MSPInterfaceMesh._create_mesh_polyface
        elif mesh_type == dxf_line_type.POLYLINES.value:
            return MSPInterfaceMesh._create_mesh_polylines
        elif mesh_type == dxf_line_type.LINES.value:
            return MSPInterfaceMesh._create_mesh_lines
        elif mesh_type == dxf_point_type.POINTS.value:
            return MSPInterfaceMesh._create_mesh_points
        return None

    @staticmethod
    def _create_mesh_points(msp, mesh, matrix, delta_xyz, dxfattribs):
        dx, dy, dz = delta_xyz
        transparency = dxfattribs.get("transparency")
        for v in mesh.vertices:
            point = msp.add_point(
                matrix @ v.co,
                dxfattribs=dxfattribs)
            point.translate(dx, dy, dz)
            if transparency:
                point.transparency = transparency

    @staticmethod
    def _create_mesh_lines(msp, mesh, matrix, delta_xyz, dxfattribs):
        dx, dy, dz = delta_xyz
        transparency = dxfattribs.get("transparency")
        for e in mesh.edges:
            line = msp.add_line(
                matrix @ mesh.vertices[e.vertices[0]].co,
                matrix @ mesh.vertices[e.vertices[1]].co,
                dxfattribs=dxfattribs)
            line.translate(dx, dy, dz)
            if transparency:
                line.transparency = transparency

    @staticmethod
    def _create_mesh_polylines(msp, mesh, matrix, delta_xyz, dxfattribs):
        dx, dy, dz = delta_xyz
        transparency = dxfattribs.get("transparency")
        for e in mesh.edges:
            polyline = msp.add_polyline3d(
                (
                    matrix @ mesh.vertices[e.vertices[0]].co,
                    matrix @ mesh.vertices[e.vertices[1]].co,
                ),
                dxfattribs=dxfattribs)
            polyline.translate(dx, dy, dz)
            if transparency:
                polyline.transparency = transparency

    @staticmethod
    def _create_mesh_polyface(msp, mesh, matrix, delta_xyz, dxfattribs):
        dx, dy, dz = delta_xyz
        polyface = msp.add_polyface(dxfattribs=dxfattribs)
        polyface.append_faces(
            [[matrix @ mesh.vertices[v].co for v in f.vertices]
                for f in mesh.polygons],
            dxfattribs=dxfattribs)
        polyface.translate(dx, dy, dz)
        if dxfattribs.get("transparency"):
            polyface.transparency = dxfattribs.get("transparency")
        polyface.optimize()

    @staticmethod
    def _create_mesh_3dfaces(msp, mesh, matrix, delta_xyz, dxfattribs):
        dx, dy, dz = delta_xyz
        transparency = dxfattribs.get("transparency")
        for f in mesh.polygons:
            face = msp.add_3dface(
                [matrix @ mesh.vertices[v].co for v in f.vertices],
                dxfattribs=dxfattribs)
            face.translate(dx, dy, dz)
            if transparency:
                face.transparency = transparency

    @staticmethod
    def _create_mesh_mesh(msp, bl_mesh, matrix, delta_xyz, dxfattribs):
        # This is the fastest way to create a Mesh entity in DXF
        dx, dy, dz = delta_xyz
        dxf_mesh = msp.add_mesh(dxfattribs)
        with dxf_mesh.edit_data() as mesh_data:
            mesh_data.vertices = [matrix @ v.co for v in bl_mesh.vertices]
            mesh_data.faces = [f.vertices for f in bl_mesh.polygons]
        dxf_mesh.translate(dx, dy, dz)
        if dxfattribs.get("transparency"):
            dxf_mesh.transparency = dxfattribs.get("transparency")


class MSPInterfaceDimensions:
    @staticmethod
    def add_aligned_dim(msp, p1, p2, distance=1, precision=2):
        line = msp.add_aligned_dim(p1=p1, p2=p2, distance=distance, dxfattribs={
                                   'layer': "Dimensions"})
        line.set_text_format(dec=precision)
        line.render(ezdxf.math.UCS(origin=(0, 0, (p1[2] + p2[2]) / 2)))
