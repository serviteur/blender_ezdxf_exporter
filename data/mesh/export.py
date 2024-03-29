import bmesh
from ezdxf_exporter.data.mesh.constants import FaceType, LineType, PointType
from ezdxf_exporter.core.export.prop import DataExporter


class MeshExporter(DataExporter):
    def __init__(self, exporter) -> None:
        super().__init__(exporter)
        self._mesh_creation_methods_dic = {
            FaceType.FACES3D.value: self._create_mesh_3dfaces,
            FaceType.MESH.value: self._create_mesh_mesh,
            FaceType.POLYFACE.value: self._create_mesh_polyface,
            LineType.POLYLINES.value: self._create_mesh_polylines,
            LineType.LINES.value: self._create_mesh_lines,
            PointType.POINTS.value: self._create_mesh_points,
        }

    def get_mesh_method(self, mesh_setting, mesh):
        # DXF Mesh object must(?) have faces (=polygons)
        # This switches the method to polylines if input mesh doesn't have any polygon
        mesh_method = self._mesh_creation_methods_dic.get(mesh_setting)
        if mesh_method == self._create_mesh_mesh and len(mesh.polygons) == 0:
            mesh_method = self._create_mesh_polylines
        return mesh_method

    def triangulate_if_needed(self, mesh, obj_type):
        "Make sure there is no N-Gon (not supported in DXF Faces)"
        if obj_type != "MESH" or self.exporter.settings.choice.faces_export not in (
            FaceType.FACES3D.value,
            FaceType.POLYFACE.value,
            FaceType.MESH.value,
        ):
            return
        if any(len(p.vertices) > 4 for p in mesh.polygons):
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh)
            bm.free()

    def create_mesh_point(self, layout, position, dxfattribs=None, callback=None):
        if dxfattribs is None:
            dxfattribs = {}
        point = layout.add_point(position, dxfattribs=dxfattribs)
        if callback is not None:
            callback(point)

    def _create_mesh_points(self, layout, mesh, dxfattribs, callback=None):
        for v in mesh.vertices:
            self.create_mesh_point(layout, v.co, dxfattribs, callback)

    def _create_mesh_lines(self, layout, mesh, dxfattribs, callback=None):
        for e in mesh.edges:
            line = layout.add_line(
                mesh.vertices[e.vertices[0]].co, mesh.vertices[e.vertices[1]].co, dxfattribs=dxfattribs
            )
            if callback is not None:
                callback(line)

    def _create_mesh_polylines(self, layout, mesh, dxfattribs, callback=None):
        vertices = mesh.vertices
        z_scale_export = self.exporter.settings.transform.export_scale[2]
        polyline_func = layout.add_lwpolyline if z_scale_export == 0 else layout.add_polyline3d
        new_entities = []
        if mesh.polygons:
            edges_not_part_of_a_polygon = set(tuple(sorted((e.vertices[0], e.vertices[1]))) for e in mesh.edges)
            edges_part_of_a_polygon = set()
            for p in mesh.polygons:
                edges_part_of_a_polygon.update(tuple(sorted((k[0], k[1]))) for k in p.edge_keys)
                polyline = polyline_func([vertices[v_idx].co for v_idx in p.vertices], dxfattribs=dxfattribs)
                polyline.dxf.flags += 1  # Close Polyline
                new_entities.append(polyline)
            edges_not_part_of_a_polygon.difference_update(edges_part_of_a_polygon)
            for v1, v2 in edges_not_part_of_a_polygon:
                polyline = polyline_func((vertices[v1].co, vertices[v2].co), dxfattribs=dxfattribs)
                new_entities.append(polyline)
        else:
            for e in mesh.edges:
                polyline = polyline_func(
                    (vertices[e.vertices[0]].co, vertices[e.vertices[1]].co),
                    dxfattribs=dxfattribs,
                )
                new_entities.append(polyline)
        if callback is not None:
            for entity in new_entities:
                callback(entity)

    def _create_mesh_polyface(self, layout, mesh, dxfattribs, callback=None):
        if len(mesh.polygons) > 0:
            polyface = layout.add_polyface(dxfattribs=dxfattribs)
            polyface.append_faces(
                [[mesh.vertices[v].co for v in f.vertices] for f in mesh.polygons], dxfattribs=dxfattribs
            )
            if callback is not None:
                callback(polyface)

    def _create_mesh_3dfaces(self, layout, mesh, dxfattribs, callback=None):
        for f in mesh.polygons:
            face_3D = layout.add_3dface([mesh.vertices[v].co for v in f.vertices], dxfattribs=dxfattribs)
            if callback is not None:
                callback(face_3D)

    def _create_mesh_mesh(self, layout, mesh, dxfattribs, callback=None):
        if len(mesh.polygons) > 0:
            dxf_mesh = layout.add_mesh(dxfattribs)
            with dxf_mesh.edit_data() as mesh_data:
                mesh_data.vertices = [v.co for v in mesh.vertices]
                mesh_data.faces = [f.vertices for f in mesh.polygons]
            if callback is not None:
                callback(dxf_mesh)

    @classmethod
    def get_evaluated_mesh(cls, obj, context):
        return obj.evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
