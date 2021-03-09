from mathutils import Matrix, Vector
import ezdxf
from .shared_maths import (
    rgb_to_hex,
    parent_lookup,
)
from .modelspace import (
    MSPInterfaceMesh,
    MSPInterfaceColor,
    create_layer_if_needed_and_get_name,
)
from . shared_properties import (
    entity_layer,
)


class DXFExporter:
    supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

    def __init__(self, debug_mode=False):
        self.doc = ezdxf.new(dxfversion="R2010")  # Create new document
        self.doc.header['$INSUNITS'] = 6  # Insertion units : Meters
        self.doc.header['$MEASUREMENT'] = 1  # Metric system
        # See https://ezdxf.readthedocs.io/en/stable/concepts/units.html
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

        # Get all collections of the scene and their parents in a dict
        coll_parents = parent_lookup(context.scene.collection) \
            if settings.entity_layer_to == entity_layer.COLLECTION.value \
                and settings.entity_layer_color \
            else None

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
                                      settings=settings,
                                      coll_parents=coll_parents)
                else:
                    block = self.doc.blocks.new(name=data.name)
                    self.write_object(obj=objs[0],
                                      layout=block,
                                      context=context,
                                      settings=settings,
                                      use_matrix=False,
                                      coll_parents=coll_parents)
                    [self.instantiate_block(block=block,
                                            context=context,
                                            settings=settings,
                                            obj=obj)
                     for obj in objs]
        else:
            [self.write_object(obj=obj,
                               layout=self.msp,
                               context=context,
                               settings=settings,
                               coll_parents=coll_parents) for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported : {self.exported_objects} Objects")
            self.log.append(
                f"NOT Exported : {self.not_exported_objects} Objects")

    def instantiate_block(self, block, context, settings, obj, coll_parents=None):
        matrix = obj.matrix_world
        scale = matrix.to_scale()
        depsgraph = context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)
        dxfattribs = {
            'layer': create_layer_if_needed_and_get_name(self.doc.layers, context, obj, settings.entity_layer_to, settings.entity_layer_transparency, coll_parents=coll_parents),
            'color': MSPInterfaceColor.get_ACI_color(settings.entity_color_to),
            'xscale': scale[0],
            'yscale': scale[1],
            'zscale': scale[2],
        }
        export_obj.rotation_mode = 'AXIS_ANGLE'
        raa = export_obj.rotation_axis_angle
        ucs = ezdxf.math.UCS(origin=matrix.to_translation()).rotate(
            (raa[1], raa[2], raa[3]), raa[0])
        blockref = self.msp.add_blockref(
            block.name, insert=(0, 0, 0), dxfattribs=dxfattribs)
        blockref.transform(ucs.matrix)
        blockref.translate(
            settings.delta_xyz[0], settings.delta_xyz[1], settings.delta_xyz[2])

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
            coll_parents=None,
    ):

        depsgraph = context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)

        dxfattribs = {
            'color': MSPInterfaceColor.get_ACI_color(settings.entity_color_to)
        }
        
        if not settings.entity_layer_separate:
            dxfattribs['layer'] = create_layer_if_needed_and_get_name(
                self.doc.layers, 
                context, 
                obj, 
                settings.entity_layer_to, 
                settings.entity_layer_transparency, 
                coll_parents)
        
        obj_color, obj_alpha = MSPInterfaceColor.get_color(
            context, obj, settings.entity_color_to, coll_parents)
        if (obj_alpha or obj_alpha == 0) and settings.entity_color_transparency:
            dxfattribs['transparency'] = 1 - obj_alpha
        if obj_color and dxfattribs['color'] == 257:
            dxfattribs['true_color'] = int(rgb_to_hex(obj_color, 256), 16)

        self.export_mesh(
            layout,
            obj,
            export_obj,
            use_matrix,
            dxfattribs,
            settings,
            context,
            coll_parents)
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def export_mesh(self, layout, base_obj, export_obj, use_matrix, dxfattribs, settings, context, coll_parents=None):
        mesh = export_obj.to_mesh()

        matrix = base_obj.matrix_world if use_matrix else Matrix()
        if settings.export_scale != (1, 1, 1):
            mx = Matrix.Scale(settings.export_scale[0], 4, (1, 0, 0))
            my = Matrix.Scale(settings.export_scale[1], 4, (0, 1, 0))
            mz = Matrix.Scale(settings.export_scale[2], 4, (0, 0, 1))
            matrix = mx @ my @ mz @ matrix
        delta_xyz = settings.delta_xyz if use_matrix else Vector((0, 0, 0))

        for i, mesh_creation_method in enumerate((
                MSPInterfaceMesh.create_mesh(settings.lines_export),
                MSPInterfaceMesh.create_mesh(settings.points_export),
                MSPInterfaceMesh.create_mesh(settings.faces_export),
        )):
            if mesh_creation_method is None:
                continue
            if i == 2:  # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                MSPInterfaceMesh.triangulate_if_needed(
                    mesh, base_obj.type, settings.faces_export)
            if settings.entity_layer_separate:
                if i == 0:
                    dxfattribs['layer'] = create_layer_if_needed_and_get_name(self.doc.layers, context, base_obj, settings.entity_layer_to, settings.entity_layer_transparency, coll_parents, suffix="_LINES") 
                elif i == 1:
                    dxfattribs['layer'] = create_layer_if_needed_and_get_name(self.doc.layers, context, base_obj, settings.entity_layer_to, settings.entity_layer_transparency, coll_parents, suffix="_POINTS") 
                elif i == 2:
                    dxfattribs['layer'] = create_layer_if_needed_and_get_name(self.doc.layers, context, base_obj, settings.entity_layer_to, settings.entity_layer_transparency, coll_parents, suffix="_FACES") 
            mesh_creation_method(
                layout,
                mesh,
                matrix,
                delta_xyz,
                dxfattribs.copy())

    def export_file(self, path):
        self.doc.entitydb.purge()
        try:
            self.doc.saveas(path)
            return True
        except PermissionError:
            return False
        except FileNotFoundError:
            return False
