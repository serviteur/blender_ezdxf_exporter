from mathutils import Matrix, Vector
import bmesh
from ..shared_properties import (
    dxf_face_type,
    dxf_line_type,
    dxf_point_type,
)
from ..shared_maths import rgb_to_hex
from .layout_interface import LayoutInterface


class LayoutInterfaceMesh(LayoutInterface):
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

    # TODO factory methods
    def _create_mesh_points(self, msp, mesh, matrix, dxfattribs):
        dx, dy, dz = self.exporter.settings.delta_xyz
        transparency = dxfattribs.get("transparency")
        for v in mesh.vertices:
            point = msp.add_point(
                matrix @ v.co,
                dxfattribs=dxfattribs)
            point.translate(dx, dy, dz)
            if transparency:
                point.transparency = transparency

    def _create_mesh_lines(self, msp, mesh, matrix, dxfattribs):
        dx, dy, dz = self.exporter.settings.delta_xyz
        transparency = dxfattribs.get("transparency")
        for e in mesh.edges:
            line = msp.add_line(
                matrix @ mesh.vertices[e.vertices[0]].co,
                matrix @ mesh.vertices[e.vertices[1]].co,
                dxfattribs=dxfattribs)
            line.translate(dx, dy, dz)
            if transparency:
                line.transparency = transparency

    def _create_mesh_polylines(self, msp, mesh, matrix, dxfattribs):
        dx, dy, dz = self.exporter.settings.delta_xyz
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

    def _create_mesh_polyface(self, msp, mesh, matrix, dxfattribs):
        dx, dy, dz = self.exporter.settings.delta_xyz
        polyface = msp.add_polyface(dxfattribs=dxfattribs)
        polyface.append_faces(
            [[matrix @ mesh.vertices[v].co for v in f.vertices]
                for f in mesh.polygons],
            dxfattribs=dxfattribs)
        polyface.translate(dx, dy, dz)
        if dxfattribs.get("transparency"):
            polyface.transparency = dxfattribs.get("transparency")
        polyface.optimize()

    def _create_mesh_3dfaces(self, msp, mesh, matrix, dxfattribs):
        dx, dy, dz = self.exporter.settings.delta_xyz
        transparency = dxfattribs.get("transparency")
        for f in mesh.polygons:
            face = msp.add_3dface(
                [matrix @ mesh.vertices[v].co for v in f.vertices],
                dxfattribs=dxfattribs)
            face.translate(dx, dy, dz)
            if transparency:
                face.transparency = transparency

    def _create_mesh_mesh(self, msp, bl_mesh, matrix, dxfattribs):
        # This is the fastest way to create a Mesh entity in DXF
        dx, dy, dz = self.exporter.settings.delta_xyz
        dxf_mesh = msp.add_mesh(dxfattribs)
        with dxf_mesh.edit_data() as mesh_data:
            mesh_data.vertices = [matrix @ v.co for v in bl_mesh.vertices]
            mesh_data.faces = [f.vertices for f in bl_mesh.polygons]
        dxf_mesh.translate(dx, dy, dz)
        if dxfattribs.get("transparency"):
            dxf_mesh.transparency = dxfattribs.get("transparency")

    def write_object(self, obj, layout=None, use_matrix=True):
        if layout is None:
            layout = self.exporter.msp
        exp = self.exporter
        depsgraph = exp.context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)

        dxfattribs = {
            'color': exp.interface_color.get_ACI_color()
        }

        if not exp.settings.entity_layer_separate:
            dxfattribs['layer'] = exp.interface_layer.create_layer_if_needed_and_get_name(
                obj)

        obj_color, obj_alpha = exp.interface_color.get_color(obj)
        if (obj_alpha or obj_alpha == 0) and exp.settings.entity_color_transparency:
            dxfattribs['transparency'] = 1 - obj_alpha
        if obj_color and dxfattribs['color'] == 257:
            dxfattribs['true_color'] = int(rgb_to_hex(obj_color, 256), 16)

        self.export_mesh(layout, obj, export_obj, use_matrix, dxfattribs)
        if exp.debug_mode:
            exp.log.append(f"{obj.name} WAS exported.")
            exp.exported_objects += 1

    def export_mesh(self, layout, base_obj, export_obj, use_matrix, dxfattribs):
        exp = self.exporter
        settings = exp.settings
        mesh = export_obj.to_mesh()

        matrix = base_obj.matrix_world if use_matrix else Matrix()
        if settings.export_scale != (1, 1, 1):
            mx = Matrix.Scale(settings.export_scale[0], 4, (1, 0, 0))
            my = Matrix.Scale(settings.export_scale[1], 4, (0, 1, 0))
            mz = Matrix.Scale(settings.export_scale[2], 4, (0, 0, 1))
            matrix = mx @ my @ mz @ matrix
        delta_xyz = settings.delta_xyz if use_matrix else Vector(
            (0, 0, 0))

        for i, mesh_creation_method in enumerate((
                self.mesh_creation_methods_dic.get(settings.lines_export),
                self.mesh_creation_methods_dic.get(settings.points_export),
                self.mesh_creation_methods_dic.get(settings.faces_export),
        )):
            if mesh_creation_method is None:
                continue
            if i == 2:  # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                exp.interface_mesh.triangulate_if_needed(mesh, base_obj.type)
            if settings.entity_layer_separate:
                if i == 0:
                    dxfattribs['layer'] = exp.interface_layer.create_layer_if_needed_and_get_name(
                        base_obj, suffix="_LINES")
                elif i == 1:
                    dxfattribs['layer'] = exp.interface_layer.create_layer_if_needed_and_get_name(
                        base_obj, suffix="_POINTS")
                elif i == 2:
                    dxfattribs['layer'] = exp.interface_layer.create_layer_if_needed_and_get_name(
                        base_obj, suffix="_FACES")
            mesh_creation_method(layout, mesh, matrix, dxfattribs.copy())
