import ezdxf
from .managers import (
    block_manager,
    color_manager,
    dimension_manager,
    layer_manager,
    mesh_manager,
    transform_manager,
    text_manager
)


class DXFExporter:
    supported_types = ('MESH', 'CURVE', 'META', 'SURFACE', 'FONT') 

    def __init__(self, context, settings, objects, coll_parents):
        self.doc = ezdxf.new(dxfversion="R2010")  # Create new document
        self.doc.header['$INSUNITS'] = 6  # Insertion units : Meters
        self.doc.header['$MEASUREMENT'] = 1  # Metric system
        # See https://ezdxf.readthedocs.io/en/stable/concepts/units.html
        self.msp = self.doc.modelspace()  # Access to dxf Modelspace

        self.context = context
        self.settings = settings
        self.objects = [o for o in objects if o.type in self.supported_types]
        self.coll_parents = coll_parents

        self.block_mgr = block_manager.BlockManager(self)
        self.mesh_mgr = mesh_manager.MeshManager(self)
        self.color_mgr = color_manager.ColorManager(self)
        self.layer_mgr = layer_manager.LayerManager(self)
        self.dimension_mgr = dimension_manager.DimensionManager(self)
        self.transform_mgr = transform_manager.TransformManager(self)
        self.text_mgr = text_manager.TextManager(self)

        self.debug_mode = settings.verbose
        self.log = []
        self.exported_objects = 0

    def write_file(self, path):
        "Saves the File and returns True if successful, False if Error"
        try:
            self.doc.saveas(path)
            return True
        except PermissionError:
            return False
        except FileNotFoundError:
            return False

    def write_object(self, obj, layout=None, use_matrix=True):
        if layout is None:
            layout = self.msp
        dxfattribs = {}
        settings = self.settings

        self.color_mgr.populate_dxfattribs(obj, dxfattribs)
        evaluated_mesh = self.mesh_mgr.get_evaluated_mesh(obj)
        i = -1
        for suffix, mesh_setting in zip(
            ("_POINTS", "_LINES", "_FACES"),
            (settings.geometry_settings.points_export, settings.geometry_settings.lines_export, settings.geometry_settings.faces_export)
        ):
            i += 1
            mesh_method = self.mesh_mgr.mesh_creation_methods_dic.get(
                mesh_setting)
            if mesh_method is None:
                continue
            self.layer_mgr.populate_dxfattribs(
                obj,
                dxfattribs,
                suffix=suffix if settings.layer_settings.entity_layer_separate[2 - i] else "",
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

    def write_block(self, block, obj):
        dxfattribs = {}
        for mgr in (self.color_mgr, self.layer_mgr):
            mgr.populate_dxfattribs(obj, dxfattribs)
        self.block_mgr.instantiate_block(block, obj)

    def write_objects(self):
        if self.settings.geometry_settings.use_blocks:
            blocks_dic, not_blocks = self.block_mgr.initialize_blocks()
            [self.write_object(obj) for obj in not_blocks]
            for obj, (block, _) in blocks_dic.items():
                self.write_object(obj=obj, layout=block, use_matrix=False)
            for block, objs in blocks_dic.values():
                [self.write_block(block, obj) for obj in objs]
        else:
            [self.write_object(obj) for obj in self.objects]
        if self.debug_mode:
            self.log.append(f"Exported {self.exported_objects} Objects")

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
