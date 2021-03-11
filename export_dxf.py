from .settings.data_settings import (
    FaceType,
    LineType,
    PointType,
    EmptyType,
    TextType,
    CameraType,
)
import ezdxf
from .managers import (
    block_manager,
    color_manager,
    dimension_manager,
    layer_manager,
    mesh_manager,
    transform_manager,
    text_manager,
    camera_manager,
)


class DXFExporter:
    supported_types = {'MESH', 'CURVE', 'META', 'SURFACE', 'FONT', 'EMPTY', 'CAMERA'}

    def update_supported_types(self):
        for attr, _enum, _type in (
            ("empties_export", EmptyType, 'EMPTY'),
            ("texts_export", TextType, 'FONT'),
            ("cameras_export", CameraType, 'CAMERA'),
        ):        
            if getattr(self.settings.data_settings, attr, 'No Export') == _enum.NONE.value:
                self.supported_types.discard(_type)
            else:
                self.supported_types.add(_type)

    def __init__(self, context, settings, objects, coll_parents):
        # Create new document
        self.doc = ezdxf.new(dxfversion="R2010")
        self.doc.header['$INSUNITS'] = 6  # Insertion units : Meters
        self.doc.header['$MEASUREMENT'] = 1  # Metric system
        # See https://ezdxf.readthedocs.io/en/stable/concepts/units.html
        self.msp = self.doc.modelspace()  # Access to dxf Modelspace

        self.context = context
        self.settings = settings
        self.update_supported_types()

        self.block_mgr = block_manager.BlockManager(self)
        self.mesh_mgr = mesh_manager.MeshManager(self)
        self.color_mgr = color_manager.ColorManager(self)
        self.layer_mgr = layer_manager.LayerManager(self)
        self.dimension_mgr = dimension_manager.DimensionManager(self)
        self.transform_mgr = transform_manager.TransformManager(self)
        self.text_mgr = text_manager.TextManager(self)
        self.camera_mgr = camera_manager.CameraManager(self)

        self.objects = [o for o in objects if o.type in self.supported_types]

        self.objects_text = []
        self.objects_empty_blocks = []
        self.objects_camera = []

        for attr, value, _type, container in (
            ("texts_export", TextType.MESH.value, 'FONT', self.objects_text),
            ("empties_export", EmptyType.POINT.value, 'EMPTY', self.objects_empty_blocks),
            ("cameras_export", CameraType.NONE.value, 'CAMERA', self.objects_camera),
        ):
            export_as = getattr(self.settings.data_settings, attr) == value
            for i in range(len(self.objects) - 1, -1, -1):
                if self.objects[i].type == _type and not export_as:
                    container.append(self.objects.pop(i))

        self.coll_parents = coll_parents

        self.debug_mode = settings.verbose
        self.log = []
        self.exported_objects = 0

    def write_file(self, path):
        "Saves the File and returns True if successful, False if Error"
        try:
            self.doc.saveas(path)
            return True
        except (PermissionError, FileNotFoundError):
            return False

    def get_dxf_attribs(self, obj, entity_type=None):
        dxfattribs = {}
        for mgr in (self.color_mgr, self.layer_mgr):
            mgr.populate_dxfattribs(obj, dxfattribs, entity_type=entity_type)
        return dxfattribs

    def write_objects(self):
        for text in self.objects_text:
            self.text_mgr.write_text(
                self.msp,
                text,
                self.transform_mgr.get_matrix(text),
                self.transform_mgr.get_rotation_axis_angle(text),
                self.get_dxf_attribs(text, TextType))

        if self.objects_empty_blocks:
            empty_block = self.block_mgr.initialize_block("Empty")
            self.mesh_mgr.create_mesh_point(empty_block, (0, 0, 0))
            # TODO : Add custom properties as Block attributes
            for empty in self.objects_empty_blocks:
                self.write_block(empty_block, empty, EmptyType)

        if self.settings.data_settings.use_blocks:
            blocks_dic, not_blocks = self.block_mgr.initialize_blocks()
            [self.write_object(obj) for obj in not_blocks]
            for obj, (block, _) in blocks_dic.items():
                self.write_object(obj=obj, layout=block, use_matrix=False)
            for block, objs in blocks_dic.values():
                [self.write_block(block, obj) for obj in objs]
        else:
            [self.write_object(obj) for obj in self.objects]

        for camera in self.objects_camera:
            self.camera_mgr.initialize_camera(camera)

        if self.debug_mode:
            self.log.append(f"Exported {self.exported_objects} Objects")

    def write_object(self, obj, layout=None, use_matrix=True):
        if layout is None:
            layout = self.msp
        dxfattribs = {}
        settings = self.settings
        data_settings = settings.data_settings

        if obj.type == 'EMPTY':
            self.mesh_mgr.create_mesh_point(self.msp, obj.location, self.get_dxf_attribs(obj, EmptyType))
        else:
            self.color_mgr.populate_dxfattribs(obj, dxfattribs)
            evaluated_mesh = self.mesh_mgr.get_evaluated_mesh(obj)
            i = -1
            for mesh_type, mesh_setting in (
                (PointType, data_settings.points_export),
                (LineType, data_settings.lines_export),
                (FaceType, data_settings.faces_export),
            ):
                i += 1
                mesh_method = self.mesh_mgr.mesh_creation_methods_dic.get(
                    mesh_setting)
                if mesh_method is None:
                    continue
                self.layer_mgr.populate_dxfattribs(
                    obj,
                    dxfattribs,
                    entity_type=mesh_type,
                    override=settings.layer_settings.entity_layer_links[2 - i])
                if i == 2:
                    # Triangulate to prevent N-Gons. Do it last to preserve geometry for lines
                    self.mesh_mgr.triangulate_if_needed(evaluated_mesh, obj.type)
                mesh_method(
                    self.msp if layout is None else layout,
                    evaluated_mesh,
                    self.transform_mgr.get_matrix(obj, use_matrix),
                    use_matrix,
                    dxfattribs.copy())
        if self.debug_mode:
            self.log.append(f"{obj.name} WAS exported.")
            self.exported_objects += 1

    def write_block(self, block, obj, entity_type=None):
        self.block_mgr.instantiate_block(
            block,
            obj,
            self.transform_mgr.get_matrix(obj),
            self.transform_mgr.get_rotation_axis_angle(obj),
            self.get_dxf_attribs(obj, entity_type))

    def write_dimensions(self, strokes):
        for s in strokes:
            # TODO : Angle dimensions
            if len(s.points) != 2:
                continue
            self.dimension_mgr.add_aligned_dim(
                s.points[0].co, s.points[1].co, 5)

    def export_file(self, path):
        self.doc.entitydb.purge()
        return self.write_file(path)
