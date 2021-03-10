from time import time
import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    PointerProperty, 
    StringProperty,
    BoolProperty,
)
from bpy.types import (
    Operator,
)

from .export_dxf import DXFExporter
from .shared_maths import(
    parent_lookup,
)
from .settings.layer_settings import (
    LayerSettings,
    entity_layer,
)
from .settings.data_settings import DataSettings
from .settings.color_settings import ColorSettings
from .settings.transform_settings import TransformSettings


class DXFExporter_OT_Export(Operator, ExportHelper):
    """File selection operator to export objects in DXF file"""
    bl_idname = "dxf_exporter.export"
    bl_label = "Export As DXF"

    filename_ext = ".dxf"

    filter_glob: StringProperty(
        default="*.dxf",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath: StringProperty(name="File Name",
                             description="filepath",
                             default="",
                             maxlen=1024,
                             options={'ANIMATABLE'},
                             subtype='NONE')

    layer_settings: PointerProperty(type=LayerSettings)
    data_settings: PointerProperty(type=DataSettings)
    color_settings: PointerProperty(type=ColorSettings)
    transform_settings: PointerProperty(type=TransformSettings)

    only_selected: BoolProperty(
        name="Export Only Selected Objects",
        default=True,
        description="What object will be exported? Only selected / All objects")

    use_dimensions: BoolProperty(
        name="Export Dimensions",
        description="Export Dimensions extracted from the built-in Measure Tool\nWarning : Works only with XY Planar dimensions",
        default=True,
    )

    verbose: BoolProperty(
        name="Verbose",
        default=False,
        description="Run the exporter in debug mode.  Check the console for output")

    def execute(self, context):
        start_time = time()
        exporter = DXFExporter(
            context=context,
            settings=self,
            objects=context.selected_objects if self.only_selected else context.scene.objects,
            coll_parents=parent_lookup(context.scene.collection)
            if self.layer_settings.entity_layer_to == entity_layer.COLLECTION.value
            and self.layer_settings.entity_layer_color
            else None
        )
        if not exporter.write_file(self.filepath):
            self.report(
                {'ERROR'}, f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)")
            return {'FINISHED'}
        exporter.write_objects()
        if self.use_dimensions:
            try:
                exporter.write_dimensions(
                    bpy.data.grease_pencils["Annotations"].layers['RulerData3D'].frames[0].strokes)
            except KeyError:
                self.report(
                    {'ERROR'}, "Could not export Dimensions. Layer 'RulerData3D' not found in Annotations Layers")

        if exporter.export_file(self.filepath):
            self.report(
                {'INFO'}, f"Export Succesful : {self.filepath} in {round(time() - start_time, 2)} sec.")
        else:
            self.report(
                {'ERROR'}, f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)")
        if self.verbose:
            for line in exporter.log:
                print(line)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Miscellaneous")
        misc_box = layout.box()
        misc_box.prop(self, "only_selected")
        dimensions_available = 'Annotations' in bpy.data.grease_pencils and 'RulerData3D' in bpy.data.grease_pencils[
            "Annotations"].layers
        dim_row = misc_box.row()
        dim_row.prop(self, "use_dimensions")
        dim_row.enabled = dimensions_available
        if not dimensions_available:
            self.use_dimensions = False

        self.data_settings.draw(layout)
        self.layer_settings.draw(layout)
        self.color_settings.draw(layout)
        self.transform_settings.draw(layout)

        layout.prop(self, "verbose")


def menu_func_export(self, context):
    self.layout.operator(DXFExporter_OT_Export.bl_idname,
                         text="Drawing Interchange File (.dxf)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
