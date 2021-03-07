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
