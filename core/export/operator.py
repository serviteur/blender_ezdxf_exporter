from time import time
import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    StringProperty,
    BoolProperty,
)
from .main import DXFExporter
from ezdxf_exporter.core.shared_maths import parent_lookup
from ezdxf_exporter.data.layer.constants import EntityLayer
from ezdxf_exporter.data.choice.prop import DataSettings
from ezdxf_exporter.core.settings.prop import Settings
from .ui import draw_op


class DXFEXPORTER_OT_Export(bpy.types.Operator, ExportHelper):
    """File selection operator to export objects in DXF file"""

    bl_idname = "dxf_exporter.export"
    bl_label = "Export As DXF"

    filename_ext = ".dxf"

    filter_glob: StringProperty(
        default="*.dxf",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath: StringProperty(
        name="File Name", description="filepath", default="", maxlen=1024, options={"ANIMATABLE"}, subtype="NONE"
    )

    verbose: BoolProperty(
        name="Debug", default=False, description="Run the exporter in debug mode.\nCheck the console for output"
    )
    settings: bpy.props.PointerProperty(type=Settings)

    def invoke(self, context, event):
        self.settings.entities.add()  # First one will be the "Default" properties
        for customizable_entity_prop in DataSettings.sub_layers_suffixes:
            self.settings.entities.add().id = customizable_entity_prop.__name__
        for entity_settings in self.settings.entities:
            entity_settings.set_default(context)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        start_time = time()
        exporter = DXFExporter(
            context=context,
            settings=self.settings,
            objects=self.settings.get_objects(context),
            coll_parents=parent_lookup(context.scene.collection)
            if self.settings.default_layer.entity_layer_to == EntityLayer.COLLECTION.value
            and self.settings.default_layer.entity_layer_color != "2"
            else None,
        )
        if not exporter.write_file(self.filepath):
            self.report(
                {"ERROR"},
                f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)",
            )
            return {"FINISHED"}

        exporter.export_materials_as_layers()
        exporter.filter_objects()
        exporter.write_objects()
        if self.settings.choice.use_dimensions:
            try:
                exporter.write_dimensions(
                    bpy.data.grease_pencils["Annotations"].layers["RulerData3D"].frames[0].strokes
                )
            except KeyError:
                self.report(
                    {"ERROR"}, "Could not export Dimensions. Layer 'RulerData3D' not found in Annotations Layers"
                )

        if exporter.export_file(self.filepath):
            self.report({"INFO"}, f"Export Succesful : {self.filepath} in {round(time() - start_time, 2)} sec.")
        else:
            self.report(
                {"ERROR"},
                f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)",
            )
        if self.verbose:
            for line in exporter.log:
                print(line)

        return {"FINISHED"}

    def draw(self, context):
        draw_op(self, context)
