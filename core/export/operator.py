from time import time
import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    PointerProperty,
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from .main import DXFExporter
from ezdxf_exporter.core.shared_maths import parent_lookup
from ezdxf_exporter.data.layer.constants import EntityLayer
from ezdxf_exporter.data.choice.prop import DataSettings
from ezdxf_exporter.data.layer.prop import GlobalLayerSettings
from ezdxf_exporter.data.transform.prop import TransformSettings
from ezdxf_exporter.data.filter.prop import (
    MiscSettings,
    ExportObjects,
    ExcludedObject,
)
from ezdxf_exporter.data.text.prop import TextSettings
from .prop import EntityProperties
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

    layer_global_settings: PointerProperty(type=GlobalLayerSettings)
    data_settings: PointerProperty(type=DataSettings)
    transform_settings: PointerProperty(type=TransformSettings)
    misc_settings: PointerProperty(type=MiscSettings)
    # Note : The 1st element is the default settings if no entity overrides it
    entities_settings: CollectionProperty(type=EntityProperties)
    text_settings: PointerProperty(type=TextSettings)

    verbose: BoolProperty(
        name="Debug", default=False, description="Run the exporter in debug mode.\nCheck the console for output"
    )

    def get_objects(self, context):
        export_setting = self.misc_settings.export_objects
        exclude_setting = self.misc_settings.export_excluded
        if export_setting == ExportObjects.SELECTED.value:
            return context.selected_objects
        elif export_setting == ExportObjects.SCENE.value:
            if exclude_setting == ExcludedObject.NONE:
                return [
                    o
                    for o in context.scene.objects
                    if not context.view_layer.layer_collection.children[o.users_collection[0].name].exclude
                    and not o.hide_viewport
                    and not o.hide_get()
                ]
            else:
                return context.scene.objects
        elif export_setting == ExportObjects.ALL.value:
            if exclude_setting == ExcludedObject.NONE:
                return [o for o in bpy.data.objects if not o.hide_viewport and not o.hide_get()]
            else:
                return bpy.data.objects

    def invoke(self, context, event):
        self.entities_settings.add()  # First one will be the "Default" properties
        for customizable_entity_prop in DataSettings.sub_layers_suffixes:
            self.entities_settings.add().id = customizable_entity_prop.__name__
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        start_time = time()
        exporter = DXFExporter(
            context=context,
            settings=self,
            objects=self.get_objects(context),
            coll_parents=parent_lookup(context.scene.collection)
            if self.default_layer_settings.entity_layer_to == EntityLayer.COLLECTION.value
            and self.default_layer_settings.entity_layer_color != "2"
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
        if self.data_settings.use_dimensions:
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

    @property
    def default_layer_settings(self):
        return self.entities_settings[0].layer_settings

    @property
    def default_color_settings(self):
        return self.entities_settings[0].color_settings

    @property
    def default_entity_settings(self):
        return self.entities_settings[0]

    def get_entity_settings(self, entity_type):
        if hasattr(entity_type, "__name__"):
            for setting in self.entities_settings:
                if setting.id == entity_type.__name__:
                    if setting.use_default:
                        return self.default_entity_settings
                    return setting
        return self.default_entity_settings
