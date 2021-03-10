from mathutils import Matrix, Vector
import bmesh
from ..shared_properties import (
    dxf_face_type,
    dxf_line_type,
    dxf_point_type, entity_color,
)
from ..shared_maths import rgb_to_hex
from .manager import Manager


class MeshManager(Manager):
    def __init__(self, exporter) -> None:
        super().__init__(exporter)
        self.mesh_creation_methods_dic = {
            dxf_face_type.FACES3D.value: self._create_mesh_3dfaces,
            dxf_face_type.MESH.value: self._create_mesh_mesh,
            dxf_face_type.POLYFACE.value: self._create_mesh_polyface,
            dxf_line_type.POLYLINES.value: self._create_mesh_polylines,
            dxf_line_type.LINES.value: self._create_mesh_lines,
            dxf_point_type.POINTS.value: self._create_mesh_points,
        }

    def triangulate_if_needed(self, mesh, obj_type):
        # Make sure there is no N-Gon (not supported in DXF Faces)
        if obj_type != 'MESH' or self.exporter.settings.faces_export not in (
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

    def _create_mesh_points(self, layout, mesh, matrix, use_matrix, dxfattribs):
        for v in mesh.vertices:
            self.create_and_transform_entity(
                lambda: layout.add_point(
                    matrix @ v.co,
                    dxfattribs=dxfattribs),
                use_matrix, dxfattribs)

    def _create_mesh_lines(self, layout, mesh, matrix, use_matrix, dxfattribs):
        for e in mesh.edges:
            self.create_and_transform_entity(
                lambda: layout.add_line(
                    matrix @ mesh.vertices[e.vertices[0]].co,
                    matrix @ mesh.vertices[e.vertices[1]].co,
                    dxfattribs=dxfattribs),
                use_matrix, dxfattribs)

    def _create_mesh_polylines(self, layout, mesh, matrix, use_matrix, dxfattribs):
        for e in mesh.edges:
            self.create_and_transform_entity(
                lambda: layout.add_polyline3d(
                    (matrix @ mesh.vertices[e.vertices[0]].co,
                     matrix @ mesh.vertices[e.vertices[1]].co,),
                    dxfattribs=dxfattribs),
                use_matrix, dxfattribs)

    def _create_mesh_polyface(self, layout, mesh, matrix, use_matrix, dxfattribs):
        def entity_func():
            polyface = layout.add_polyface(dxfattribs=dxfattribs)
            polyface.append_faces(
                [[matrix @ mesh.vertices[v].co for v in f.vertices]
                    for f in mesh.polygons],
                dxfattribs=dxfattribs)
            return polyface
        self.create_and_transform_entity(entity_func, use_matrix, dxfattribs)

    def _create_mesh_3dfaces(self, layout, mesh, matrix, use_matrix, dxfattribs):
        for f in mesh.polygons:
            self.create_and_transform_entity(
                lambda: layout.add_3dface(
                    [matrix @ mesh.vertices[v].co for v in f.vertices],
                    dxfattribs=dxfattribs),
                use_matrix, dxfattribs)

    def _create_mesh_mesh(self, layout, mesh, matrix, use_matrix, dxfattribs):
        def entity_func():
            dxf_mesh = layout.add_mesh(dxfattribs)
            with dxf_mesh.edit_data() as mesh_data:
                mesh_data.vertices = [matrix @ v.co for v in mesh.vertices]
                mesh_data.faces = [f.vertices for f in mesh.polygons]
            return dxf_mesh
        self.create_and_transform_entity(entity_func, use_matrix, dxfattribs)

    def create_and_transform_entity(self, entity_func, use_matrix, dxfattribs):
        entity = entity_func()
        dx, dy, dz = self.exporter.settings.delta_xyz if use_matrix else (
            0, 0, 0)
        entity.translate(dx, dy, dz)
        # TODO : Transparency should not be set here
        if dxfattribs.get("transparency"):
            entity.transparency = dxfattribs.get("transparency") / 10
        return entity

    def get_evaluated_mesh(self, obj):
        return obj.evaluated_get(self.exporter.context.evaluated_depsgraph_get()).to_mesh()
