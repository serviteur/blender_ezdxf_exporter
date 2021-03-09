from mathutils import Matrix, Vector
import ezdxf
from .shared_maths import (
    rgb_to_hex,
)
from .interface import (
    layout_interface_block, 
    layout_interface_color,
    layout_interface_dimension,
    layout_interface_layer,
    layout_interface_mesh,
)
from . shared_properties import (
    entity_layer,
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

        self.interface_block = layout_interface_block.LayoutInterfaceBlock(self)
        self.interface_mesh = layout_interface_mesh.LayoutInterfaceMesh(self)
        self.interface_color = layout_interface_color.LayoutInterfaceColor(self)
        self.interface_layer = layout_interface_layer.LayoutInterfaceLayer(self)
        self.interface_dimension = layout_interface_dimension.LayoutInterfaceDimensions(self)

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

    def write_objects(self):
        if self.settings.use_blocks:
            not_blocks = self.interface_block.instantiate_blocks()
            [self.interface_mesh.write_object(obj) for obj in not_blocks]
        else:
            [self.interface_mesh.write_object(obj) for obj in objects]
        if self.debug_mode:
            self.log.append(f"Exported {self.exported_objects} Objects")

    def write_dimensions(self, strokes):
        for s in strokes:
            # TODO : Angle dimensions
            if len(s.points) != 2:
                continue
            self.interface_dimension.add_aligned_dim(s.points[0].co, s.points[1].co, 5)

    def export_file(self, path):
        self.doc.entitydb.purge()
        return self.write_file(path)
