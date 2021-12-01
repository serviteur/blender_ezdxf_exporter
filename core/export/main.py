from typing import Dict
import ezdxf

from ezdxf_exporter.data.choice.prop import (
    CurveType,
    FaceType,
    LineType,
    PointType,
    EmptyType,
    TextType,
    CameraType,
    NO_EXPORT,
)
from ezdxf_exporter.data.block.export import BlockExporter
from ezdxf_exporter.data.color.export import ColorExporter
from ezdxf_exporter.data.dimension.export import DimensionExporter
from ezdxf_exporter.data.mesh.export import MeshExporter
from ezdxf_exporter.data.transform.export import TransformExporter
from ezdxf_exporter.data.text.export import TextExporter
from ezdxf_exporter.data.camera.export import CameraExporter
from ezdxf_exporter.data.curve.export import SplineExporter
from ezdxf_exporter.data.layer.export import LayerExporter
from ezdxf_exporter.data.unit.export import UnitExporter
from ezdxf.math import Vec3


class DXFExporter:
    supported_types = {"MESH", "CURVE", "META", "SURFACE", "FONT", "EMPTY", "CAMERA"}

    def __init__(self, context, settings, objects, coll_parents):
        self.debug_mode = False  # TODO implement debug mode
        self.log = []
        self.exported_objects = 0

        # Create new document
        self.doc = ezdxf.new(dxfversion="R2010")

        self.msp = self.doc.modelspace()  # Access to dxf Modelspace

        self.context = context
        self.settings = settings

        self.block_exporter = BlockExporter(self)
        self.mesh_exporter = MeshExporter(self)
        self.color_exporter = ColorExporter(self)
        self.layer_exporter = LayerExporter(self)
        self.dimension_exporter = DimensionExporter(self)
        self.transform_exporter = TransformExporter(self)
        self.text_exporter = TextExporter(self)
        self.camera_exporter = CameraExporter(self)
        self.spline_exporter = SplineExporter(self)
        self.unit_exporter = UnitExporter(self)

        self.update_supported_types()
        self.objects = [o for o in objects if o.type in self.supported_types]

        self.objects_text = []
        self.objects_empty_blocks = []
        self.objects_camera = []
        self.objects_curve = []

        self.coll_parents = coll_parents

    def update_supported_types(self):
        "Dynamically update supported object types. Use before filtering them"
        for attr, _type in (
            ("empties_export", "EMPTY"),
            ("texts_export", "FONT"),
            ("cameras_export", "CAMERA"),
            ("curves_export", "CURVE"),
        ):
            if getattr(self.settings.choice, attr, NO_EXPORT) == NO_EXPORT:
                self.supported_types.discard(_type)
            else:
                self.supported_types.add(_type)

    def write_file(self, path):
        "Saves the File and returns True if successful, False if Error"
        try:
            self.doc.saveas(path)
            return True
        except (PermissionError, FileNotFoundError):
            return False

    def filter_objects(self):
        "Pops objects from the objects container and populate respective pools if they aren't exported as Mesh"
        for attr, value, _type, container in (
            ("texts_export", TextType.MESH.value, "FONT", self.objects_text),
            ("empties_export", EmptyType.POINT.value, "EMPTY", self.objects_empty_blocks),
            ("cameras_export", CameraType.NONE.value, "CAMERA", self.objects_camera),
            ("curves_export", CurveType.MESH.value, "CURVE", self.objects_curve),
        ):
            export_as = getattr(self.settings.choice, attr) == value
            for i in range(len(self.objects) - 1, -1, -1):
                if self.objects[i].type == _type and not export_as:
                    container.append(self.objects.pop(i))

    def get_dxf_attribs(self, obj, entity_type=None) -> Dict[str, any]:
        """Populate dxfattribs used by most Drawing entity factor methods
        1. Adds color keys and values
        2. Adds the layer name
        """
        dxfattribs = {}
        for mgr in (self.color_exporter, self.layer_exporter):
            if not mgr.populate_dxfattribs(obj, dxfattribs, entity_type=entity_type):
                return False
        return dxfattribs

    def on_entity_created(self, base_obj, entity, dxfattribs, is_block=False):
        "Callback called when a new entity is created"
        if entity:
            if not is_block:
                dx, dy, dz = self.settings.transform.delta_xyz
                entity.translate(dx, dy, dz)
            if dxfattribs.get("transparency"):
                entity.transparency = dxfattribs.get("transparency") / 10

    def export_curves(self):
        "Export CURVE Objects as Spline Entities"
        for curve in self.objects_curve:
            dxfattribs = self.get_dxf_attribs(curve, CurveType)
            if not dxfattribs:
                continue
            self.spline_exporter.write_curve(
                self.msp,
                curve,
                self.transform_exporter.get_matrix(curve),
                # TODO : like texts, derive raa from matrix_world
                self.transform_exporter.get_rotation_axis_angle(curve),
                dxfattribs,
                callback=lambda e: self.on_entity_created(curve, e, dxfattribs),
            )

    def export_texts(self):
        "Export FONT Objects as MTEXT or TEXT entities"
        for text in self.objects_text:
            dxfattribs = self.get_dxf_attribs(text, TextType)
            if not dxfattribs:
                continue
            self.text_exporter.write_text(
                self.msp,
                text,
                self.transform_exporter.get_matrix(text),
                dxfattribs,
                callback=lambda e: self.on_entity_created(text, e, dxfattribs),
            )

    def export_empty_blocks(self):
        "Export EMPTY objects as BLOCK with 1 point entity (Else you can't select it)"
        if self.objects_empty_blocks:
            empty_block = self.block_exporter.initialize_block("Empty")
            self.mesh_exporter.create_mesh_point(empty_block, (0, 0, 0))
            # TODO : Add custom properties as Block attributes
            for empty in self.objects_empty_blocks:
                self.write_block(empty_block, empty, EmptyType)

    def export_linked_objects(self):
        "Export Linked Objects as multiple BLOCKs"
        blocks_dic, not_blocks = self.block_exporter.initialize_blocks()
        [self.write_mesh_object(obj) for obj in not_blocks]
        for obj, (block, _) in blocks_dic.items():
            # Create the BLOCK def which all linked objects will instantiate
            self.write_mesh_object(obj=obj, layout=block, is_block=True)
        for block, objs in blocks_dic.values():
            # Instantiate all linked objects from block definition
            [self.write_block(block, obj) for obj in objs]

    def export_cameras(self):
        for camera in self.objects_camera:
            # Initialize viewports from Camera (WIP)
            self.camera_exporter.initialize_camera(
                camera,
                self.settings.transform.delta_xyz,
            )

    def write_objects(self):
        self.export_curves()
        self.export_texts()
        self.export_empty_blocks()

        if self.settings.choice.use_blocks:
            self.export_linked_objects()
        else:
            # Export objects as MESH and/or LINES and/or POINTS
            [self.write_mesh_object(obj) for obj in self.objects]
        self.export_cameras()

        if self.debug_mode:
            self.log.append(f"Exported {self.exported_objects} Objects")

    def write_mesh_object(self, obj, layout=None, is_block=False):
        if layout is None:
            layout = self.msp
        dxfattribs = {}
        settings = self.settings
        data_settings = settings.choice

        if obj.type == "EMPTY":
            dxfattribs = self.get_dxf_attribs(obj, EmptyType)
            if not dxfattribs:
                return
            self.mesh_exporter.create_mesh_point(
                self.msp, obj.location, dxfattribs, callback=lambda e: self.on_entity_created(obj, e, dxfattribs)
            )
        else:
            evaluated_mesh = self.mesh_exporter.get_evaluated_mesh(obj, self.context)
            evaluated_mesh.transform(self.transform_exporter.get_matrix(obj, is_block))
            # Since Mesh Objects can be exported as Faces, Edges and Vertices
            # We loop through all three of these options
            i = -1
            for mesh_type, mesh_setting in (
                (PointType, data_settings.points_export),
                (LineType, data_settings.lines_export),
                (FaceType, data_settings.faces_export),
            ):
                i += 1
                mesh_method = self.mesh_exporter.get_mesh_method(mesh_setting, evaluated_mesh)
                if mesh_method is None:
                    continue
                self.color_exporter.populate_dxfattribs(obj, dxfattribs, mesh_type)
                if not self.layer_exporter.populate_dxfattribs(obj, dxfattribs, entity_type=mesh_type, override=True):
                    continue
                if i == 2:
                    # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                    self.mesh_exporter.triangulate_if_needed(evaluated_mesh, obj.type)
                mesh_method(
                    self.msp if layout is None else layout,
                    evaluated_mesh,
                    dxfattribs.copy(),
                    callback=lambda e: self.on_entity_created(obj, e, dxfattribs, is_block=is_block),
                )
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def write_block(self, block, obj, entity_type=None):
        dxfattribs = self.get_dxf_attribs(obj, entity_type)
        if not dxfattribs:
            return
        self.block_exporter.instantiate_block(
            block,
            self.transform_exporter.get_matrix(obj),
            self.transform_exporter.get_rotation_axis_angle(obj),
            dxfattribs,
            callback=lambda e: self.on_entity_created(obj, e, dxfattribs),
        )

        if self.debug_mode:
            self.log.append(f"{obj.name} was added as a Block")

    def write_dimensions(self, strokes):
        # TODO : Add dimensions if annotation layer is hidden in blend file
        for s in strokes:
            # TODO : Angle dimensions
            if len(s.points) != 2:
                continue
            self.dimension_exporter.add_aligned_dim(s.points[0].co, s.points[1].co, 5)

    def export_materials_as_layers(self):
        layer_settings = self.settings.layer_global
        if not layer_settings.material_layer_export:
            return
        mat_objects = self.objects if layer_settings.material_layer_export_only_selected else self.context.scene.objects
        for mats in [
            o.data.materials for o in mat_objects if o.data and hasattr(o.data, "materials") and o.data.materials
        ]:
            for mat in mats:
                self.layer_exporter.get_or_create_layer_from_mat(mat)

    def export_file(self, path):
        self.doc.entitydb.purge()
        return self.write_file(path)
