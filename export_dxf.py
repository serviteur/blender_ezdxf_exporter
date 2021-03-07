import ezdxf
import bmesh
import bpy
from .shared_properties import (
    rgb_to_hex,
    float_to_hex,
)
from .modelspace import (
    MSPInterfaceMesh,
    MSPInterfaceColor,
    get_layer_name,
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

    def can_write_file(self, path):        
        try:
            self.doc.saveas(path)
            return True
        except PermissionError:
            return False

    def write_objects(
            self,
            objects,
            context,
            faces_as,
            lines_as,
            points_as,
            layer,
            layer_separate,
            color,
            delta_xyz,
            ):
        [self.write_object(
            obj=obj,
            context=context,
            faces_as=faces_as,
            lines_as=lines_as,
            points_as=points_as,
            layer=layer,
            layer_separate=layer_separate,
            color=color,
            delta_xyz=delta_xyz,
        )
            for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")


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
            faces_as,
            lines_as,
            points_as,
            layer='0',
            layer_separate=False,
            color='BYLAYER',
            delta_xyz=(0, 0, 0),
            ):

        if not self.is_object_supported(obj):
            return

        depsgraph = context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)

        dxfattribs = {
            'layer': get_layer_name(self.doc.layers, context, obj, layer),
            'color': MSPInterfaceColor.get_ACI_color(color)
        }

        obj_color, obj_alpha = MSPInterfaceColor.get_color(context, obj, color)
        dxfattribs['transparency'] = int(float_to_hex(1 - obj_alpha), 16)
        dxfattribs['transparency'] = 50
        if dxfattribs['color'] == 257:
            dxfattribs['true_color'] = int(rgb_to_hex(obj_color, 256), 16)

        self.export_mesh(export_obj, dxfattribs, faces_as, lines_as, points_as, layer_separate, delta_xyz)
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def export_mesh(self, obj, dxfattribs, faces_as, lines_as, points_as, layer_separate, delta_xyz):
        obj_matrix_world = obj.matrix_world
        mesh = obj.to_mesh()

        layer = dxfattribs['layer']

        for i, mesh_creation_method in enumerate((
                MSPInterfaceMesh.create_mesh(lines_as),
                MSPInterfaceMesh.create_mesh(points_as), 
                MSPInterfaceMesh.create_mesh(faces_as),
        )):
            if mesh_creation_method is None:
                continue
            if i == 2: # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                MSPInterfaceMesh.triangulate_if_needed(mesh, obj.type, faces_as)
            if layer_separate:
                if i == 0:
                    dxfattribs['layer'] = layer + "_LINES"
                if i == 1:
                    dxfattribs['layer'] = layer + "_POINTS"
                if i == 2:
                    dxfattribs['layer'] = layer + "_FACES"
            mesh_creation_method(self.msp, mesh, obj_matrix_world, delta_xyz, dxfattribs.copy())



    def export_file(self, path):
        self.doc.entitydb.purge()
        try:
            self.doc.saveas(path)
            return True
        except PermissionError:
            return False
            
