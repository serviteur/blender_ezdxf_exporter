from mathutils import Matrix, Vector
from math import degrees
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
        # TODO : Log export times
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
            settings,
    ):
        objects = [o for o in objects if self.is_object_supported(o)]

        if settings.use_blocks:
            data_obj_dict = {}
            for obj in objects:
                data = obj.data
                if data in data_obj_dict:
                    data_obj_dict[data].append(obj)
                else:
                    data_obj_dict[data] = [obj]
            for data, objs in data_obj_dict.items():
                if not objs:
                    continue
                if len(objs) == 1:
                    self.write_object(obj=objs[0],
                                      layout=self.msp,
                                      context=context,
                                      settings=settings)
                else:
                    block = self.doc.blocks.new(name=data.name)
                    self.write_object(obj=objs[0],
                                      layout=block,
                                      context=context,
                                      settings=settings,
                                      use_matrix=False)
                    [self.instantiate_block(block=block,
                                            context=context,
                                            settings=settings,
                                            obj=obj)
                     for obj in objs]
        else:
            [self.write_object(obj=obj,
                               layout=self.msp,
                               context=context,
                               settings=settings) for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")

    def instantiate_block(self, block, context, settings, obj):
        matrix = obj.matrix_world
        scale = matrix.to_scale()
        euler = matrix.to_euler()
        # FIXME : Matrix fails if object is rotated along local X or Y axis.
        if euler[0] != 0 or euler[1] != 0:
            self.write_object(obj=obj,
                              layout=self.msp,
                              context=context,
                              settings=settings)
            if self.debug_mode:
                self.log.append(f"Object {obj.name} should be inserted as a block but it has a local X or Y rotation. Insert as a regular Mesh instead")
            return
        dxfattribs = {
            'layer': get_layer_name(self.doc.layers, context, obj, settings.entity_layer_to),
            'color': MSPInterfaceColor.get_ACI_color(settings.entity_color_to),
            'xscale': scale[0],
            'yscale': scale[1],
            'zscale': scale[2],
            'rotation': degrees(euler[2])
        }

        self.msp.add_blockref(
            block.name, matrix.to_translation() + settings.delta_xyz, dxfattribs=dxfattribs)
        if self.debug_mode:
            self.log.append(f"Object {obj.name} was added as a Block")

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
            layout,
            obj,
            context,
            settings,
            use_matrix=True,
    ):

        depsgraph = context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)

        dxfattribs = {
            'layer': get_layer_name(self.doc.layers, context, obj, settings.entity_layer_to),
            'color': MSPInterfaceColor.get_ACI_color(settings.entity_color_to)
        }

        obj_color, obj_alpha = MSPInterfaceColor.get_color(
            context, obj, settings.entity_color_to)
        dxfattribs['transparency'] = int(float_to_hex(1 - obj_alpha), 16)
        dxfattribs['transparency'] = 50
        if dxfattribs['color'] == 257:
            dxfattribs['true_color'] = int(rgb_to_hex(obj_color, 256), 16)

        self.export_mesh(
            layout,
            export_obj,
            use_matrix,
            dxfattribs,
            settings)
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def export_mesh(self, layout, obj, use_matrix, dxfattribs, settings):
        mesh = obj.to_mesh()

        layer = dxfattribs['layer']

        for i, mesh_creation_method in enumerate((
                MSPInterfaceMesh.create_mesh(settings.lines_export),
                MSPInterfaceMesh.create_mesh(settings.points_export),
                MSPInterfaceMesh.create_mesh(settings.faces_export),
        )):
            if mesh_creation_method is None:
                continue
            if i == 2:  # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                MSPInterfaceMesh.triangulate_if_needed(
                    mesh, obj.type, settings.faces_export)
            if settings.entity_layer_separate:
                if i == 0:
                    dxfattribs['layer'] = layer + "_LINES"
                elif i == 1:
                    dxfattribs['layer'] = layer + "_POINTS"
                elif i == 2:
                    dxfattribs['layer'] = layer + "_FACES"
            mesh_creation_method(
                layout, 
                mesh, 
                obj.matrix_world if use_matrix else Matrix(), 
                settings.delta_xyz if use_matrix else Vector((0, 0, 0)), 
                dxfattribs.copy())

    def export_file(self, path):
        self.doc.entitydb.purge()
        try:
            self.doc.saveas(path)
            return True
        except PermissionError:
            return False
