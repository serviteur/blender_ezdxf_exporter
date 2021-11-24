from typing import Dict
import ezdxf
from .settings.data_settings import (
    CurveType,
    FaceType,
    LineType,
    PointType,
    EmptyType,
    TextType,
    CameraType,
    NO_EXPORT
)
from .managers import (
    block_manager,
    color_manager,
    dimension_manager,
    layer_manager,
    mesh_manager,
    transform_manager,
    text_manager,
    camera_manager,
    spline_manager,
)
from ezdxf.math import Vec3


class DXFExporter:
    supported_types = {'MESH', 'CURVE', 'META',
                       'SURFACE', 'FONT', 'EMPTY', 'CAMERA'}

    def __init__(self, context, settings, objects, coll_parents):
        # Create new document
        self.doc = ezdxf.new(dxfversion="R2010")
        self.doc.header['$INSUNITS'] = 6  # Insertion units : Meters
        self.doc.header['$MEASUREMENT'] = 1  # Metric system
        # See https://ezdxf.readthedocs.io/en/stable/concepts/units.html
        self.msp = self.doc.modelspace()  # Access to dxf Modelspace

        self.context = context
        self.settings = settings

        self.block_mgr = block_manager.BlockManager(self)
        self.mesh_mgr = mesh_manager.MeshManager(self)
        self.color_mgr = color_manager.ColorManager(self)
        self.layer_mgr = layer_manager.LayerManager(self)
        self.dimension_mgr = dimension_manager.DimensionManager(self)
        self.transform_mgr = transform_manager.TransformManager(self)
        self.text_mgr = text_manager.TextManager(self)
        self.camera_mgr = camera_manager.CameraManager(self)
        self.spline_mgr = spline_manager.SplineManager(self)

        self.update_supported_types()
        self.objects = [o for o in objects if o.type in self.supported_types]

        self.objects_text = []
        self.objects_empty_blocks = []
        self.objects_camera = []
        self.objects_curve = []

        self.coll_parents = coll_parents

        self.debug_mode = settings.verbose
        self.log = []
        self.exported_objects = 0

    def update_supported_types(self):
        "Dynamically update supported object types. Use before filtering them"
        for attr, _type in (
            ("empties_export", 'EMPTY'),
            ("texts_export", 'FONT'),
            ("cameras_export", 'CAMERA'),
            ("curves_export", 'CURVE'),
        ):
            if getattr(self.settings.data_settings, attr, NO_EXPORT) == NO_EXPORT:
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
            ("texts_export", TextType.MESH.value, 'FONT', self.objects_text),
            ("empties_export", EmptyType.POINT.value,
             'EMPTY', self.objects_empty_blocks),
            ("cameras_export", CameraType.NONE.value, 'CAMERA', self.objects_camera),
            ("curves_export", CurveType.MESH.value, 'CURVE', self.objects_curve),
        ):
            export_as = getattr(self.settings.data_settings, attr) == value
            for i in range(len(self.objects) - 1, -1, -1):
                if self.objects[i].type == _type and not export_as:
                    container.append(self.objects.pop(i))

    def get_dxf_attribs(self, obj, entity_type=None) -> Dict[str, any]:
        """Populate dxfattribs used by most Drawing entity factor methods
        1. Adds color keys and values
        2. Adds the layer name
        """
        dxfattribs = {}
        for mgr in (self.color_mgr, self.layer_mgr):
            if not mgr.populate_dxfattribs(obj, dxfattribs, entity_type=entity_type):
                return False
        return dxfattribs

    def on_entity_created(self, base_obj, entity, dxfattribs, is_block=False):
        "Callback called when a new entity is created"
        if entity:
            if not is_block:
                dx, dy, dz = self.settings.transform_settings.delta_xyz
                entity.translate(dx, dy, dz)
            if dxfattribs.get("transparency"):
                entity.transparency = dxfattribs.get("transparency") / 10

    def export_curves(self):
        "Export CURVE Objects as Spline Entities"
        for curve in self.objects_curve:
            dxfattribs = self.get_dxf_attribs(curve, CurveType)
            if not dxfattribs:
                continue
            self.spline_mgr.write_curve(
                self.msp,
                curve,
                self.transform_mgr.get_matrix(curve),
                # TODO : like texts, derive raa from matrix_world
                self.transform_mgr.get_rotation_axis_angle(curve),
                dxfattribs,
                callback=lambda e: self.on_entity_created(curve, e, dxfattribs))

    def export_texts(self):
        "Export FONT Objects as MTEXT or TEXT entities"
        for text in self.objects_text:
            dxfattribs = self.get_dxf_attribs(text, TextType)
            if not dxfattribs:
                continue
            self.text_mgr.write_text(
                self.msp,
                text,
                self.transform_mgr.get_matrix(text),
                dxfattribs,
                callback=lambda e: self.on_entity_created(text, e, dxfattribs),
            )

    def export_empty_blocks(self):
        "Export EMPTY objects as BLOCK with 1 point entity (Else you can't select it)"
        if self.objects_empty_blocks:
            empty_block = self.block_mgr.initialize_block("Empty")
            self.mesh_mgr.create_mesh_point(empty_block, (0, 0, 0))
            # TODO : Add custom properties as Block attributes
            for empty in self.objects_empty_blocks:
                self.write_block(empty_block, empty, EmptyType)

    def export_linked_objects(self):
        "Export Linked Objects as multiple BLOCKs"
        blocks_dic, not_blocks = self.block_mgr.initialize_blocks()
        [self.write_mesh_object(obj) for obj in not_blocks]
        for obj, (block, _) in blocks_dic.items():
            # Create the BLOCK def which all linked objects will instantiate
            self.write_mesh_object(
                obj=obj, layout=block, is_block=True)
        for block, objs in blocks_dic.values():
            # Instantiate all linked objects from block definition
            [self.write_block(block, obj) for obj in objs]

    def export_cameras(self):
        for camera in self.objects_camera:
            # Initialize viewports from Camera (WIP)
            self.camera_mgr.initialize_camera(
                camera,
                self.settings.transform_settings.delta_xyz,
            )

    def write_objects(self):
        self.export_curves()
        self.export_texts()
        self.export_empty_blocks()

        if self.settings.data_settings.use_blocks:
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
        data_settings = settings.data_settings

        if obj.type == 'EMPTY':
            dxfattribs = self.get_dxf_attribs(obj, EmptyType)
            if not dxfattribs:
                return
            self.mesh_mgr.create_mesh_point(
                self.msp,
                obj.location,
                dxfattribs,
                callback=lambda e: self.on_entity_created(obj, e, dxfattribs))
        else:
            evaluated_mesh = self.mesh_mgr.get_evaluated_mesh(
                obj, self.context)
            evaluated_mesh.transform(
                self.transform_mgr.get_matrix(obj, is_block))
            # Since Mesh Objects can be exported as Faces, Edges and Vertices
            # We loop through all three of these options
            i = -1
            for mesh_type, mesh_setting in (
                (PointType, data_settings.points_export),
                (LineType, data_settings.lines_export),
                (FaceType, data_settings.faces_export),
            ):
                i += 1
                mesh_method = self.mesh_mgr.get_mesh_method(mesh_setting, evaluated_mesh)
                if mesh_method is None:
                    continue
                self.color_mgr.populate_dxfattribs(obj, dxfattribs, mesh_type)
                if not self.layer_mgr.populate_dxfattribs(
                        obj,
                        dxfattribs,
                        entity_type=mesh_type,
                        override=True):
                    continue
                if i == 2:
                    # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                    self.mesh_mgr.triangulate_if_needed(
                        evaluated_mesh, obj.type)
                mesh_method(
                    self.msp if layout is None else layout,
                    evaluated_mesh,
                    dxfattribs.copy(),
                    callback=lambda e: self.on_entity_created(obj, e, dxfattribs, is_block=is_block))
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def write_block(self, block, obj, entity_type=None):
        dxfattribs = self.get_dxf_attribs(obj, entity_type)
        if not dxfattribs:
            return
        self.block_mgr.instantiate_block(
            block,
            self.transform_mgr.get_matrix(obj),
            self.transform_mgr.get_rotation_axis_angle(obj),
            dxfattribs,
            callback=lambda e: self.on_entity_created(obj, e, dxfattribs))

        if self.debug_mode:
            self.log.append(f"{obj.name} was added as a Block")

    def write_dimensions(self, strokes):
        # TODO : Add dimensions if annotation layer is hidden in blend file
        for s in strokes:
            # TODO : Angle dimensions
            if len(s.points) != 2:
                continue
            self.dimension_mgr.add_aligned_dim(
                s.points[0].co,
                s.points[1].co,
                5)

    def export_materials_as_layers(self):
        layer_settings = self.settings.layer_global_settings
        if not layer_settings.material_layer_export:
            return
        mat_objects = self.objects if layer_settings.material_layer_export_only_selected else self.context.scene.objects
        for mats in [o.data.materials for o in mat_objects if o.data and hasattr(o.data, "materials") and o.data.materials]:
            for mat in mats:
                rgb, a = self.color_mgr._get_material_color(mat)
                self.layer_mgr.create_layer(name="MATERIAL_" + mat.name, rgb=rgb,
                                            transparency=1 - a if self.settings.default_layer_settings.entity_layer_transparency else 0)

    def export_file(self, path):
        self.doc.entitydb.purge()
        return self.write_file(path)
