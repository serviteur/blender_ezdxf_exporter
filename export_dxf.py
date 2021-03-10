import ezdxf
from .managers import (
    block_manager,
    color_manager,
    dimension_manager,
    layer_manager,
    mesh_manager,
    transform_manager,
)


class DXFExporter:
    supported_types = ('MESH', 'CURVE', 'META', 'SURFACE')

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

        self.debug_mode = settings.verbose
        # TODO : Log export times
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
        dxfattribs = {}
        self.interface_color.populate_dxfattribs(obj, dxfattribs)
        self.interface_mesh.write_object(obj, dxfattribs, layout, use_matrix)

    def write_objects(self):
        if self.settings.use_blocks:
            blocks_dic, not_blocks = self.block_mgr.initialize_blocks()
            [self.write_object(obj) for obj in not_blocks]
            for obj, (block, _) in blocks_dic.items():
                self.write_object(obj=obj, layout=block, use_matrix=False)
            for block, objs in blocks_dic.values():
                [self.interface_block.instantiate_block(block, obj) for obj in objs]
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
