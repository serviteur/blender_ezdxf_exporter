from time import time
import bpy

from bl_operators.presets import AddPresetBase
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    PointerProperty, 
    StringProperty,
    BoolProperty,
    CollectionProperty,
)
from bpy.types import (
    Operator,
    Menu,

    PropertyGroup,
)

from .export_dxf import DXFExporter
from .shared_maths import(
    parent_lookup,
)
from .settings.layer_settings import (
    LayerSettings,
    GlobalLayerSettings,
    EntityLayer,
)
from .settings.data_settings import DataSettings
from .settings.color_settings import ColorSettings
from .settings.transform_settings import TransformSettings


class EntityProperties(PropertyGroup):
    layer_settings: PointerProperty(
        name="Layer Props",
        type=LayerSettings,
    )
    color_settings: PointerProperty(
        name="Color Props",
        type=ColorSettings,
    )
    id: StringProperty(
        name="Data identifier",
        description="Unique string identifier (enum class __name__)",
    )
    use_default: BoolProperty(
        name="Use default settings",
        default=True,
    )


class DXFEXPORTER_OT_Export(Operator, ExportHelper):
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

    layer_global_settings: PointerProperty(type=GlobalLayerSettings)
    data_settings: PointerProperty(type=DataSettings)
    transform_settings: PointerProperty(type=TransformSettings)
    entities_settings: CollectionProperty(type=EntityProperties)

    only_selected: BoolProperty(
        name="Export Only Selected Objects",
        default=True,
        description="What object will be exported? Only selected / All objects")
    
    export_excluded: BoolProperty(
        name="Export Excluded / Hidden Objects",
        description="Export Objects inside Collections which are Excluded from View Layer",
        default=True,
    )

    use_dimensions: BoolProperty(
        name="Export Dimensions",
        description="Export Dimensions extracted from the built-in Measure Tool\nWarning : Works only with XY Planar dimensions",
        default=True,
    )

    verbose: BoolProperty(
        name="Debug",
        default=False,
        description="Run the exporter in debug mode.\nCheck the console for output")

    def get_objects(self, context):
        if self.only_selected:
            return context.selected_objects
        else:
            if self.export_excluded:
                return context.scene.objects
            else:
                return [o for o in context.scene.objects if not context.view_layer.layer_collection.children[o.users_collection[0].name].exclude]

    def execute(self, context):
        start_time = time()
        exporter = DXFExporter(
            context=context,
            settings=self,
            objects=self.get_objects(context),
            coll_parents=parent_lookup(context.scene.collection)
            if self.default_layer_settings.entity_layer_to == EntityLayer.COLLECTION.value
            and self.default_layer_settings.entity_layer_color
            else None
        )
        if not exporter.write_file(self.filepath):
            self.report(
                {'ERROR'}, f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)")
            return {'FINISHED'}

        exporter.export_materials_as_layers()
        exporter.filter_objects()
        exporter.write_objects()
        if self.data_settings.use_dimensions:
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

        draw_preset(self, context)
        self.data_settings.draw(layout, self.get_objects(
            context), self.entities_settings)
        layer_box = self.default_layer_settings.draw(layout)
        self.layer_global_settings.draw(layer_box)
        self.default_color_settings.draw(layout)
        self.transform_settings.draw(layout)

        layout.prop(self, "verbose")

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

def menu_func_export(self, context):
    op = self.layout.operator(DXFEXPORTER_OT_Export.bl_idname,
                         text="Drawing Interchange File (.dxf)")
    # Inefficient. Couldn't find a way to run this only once when the operator is called :
    op.entities_settings.add()  # First one will be the "Default" properties
    for customizable_entity_prop in DataSettings.sub_layers_suffixes:
        op.entities_settings.add().id = customizable_entity_prop.__name__

# Preset System courtesy
# https://blender.stackexchange.com/questions/209877/preset-system-error
# https://sinestesia.co/blog/tutorials/using-blenders-presets-in-python/
class DXFEXPORTER_MT_Preset(Menu):
    bl_label = "DXF Export"
    preset_subdir = DXFEXPORTER_OT_Export.bl_idname
    preset_operator = "script.execute_preset"

    def draw(self, context):
        self.draw_preset(context)


class DXFEXPORTER_OT_Preset(AddPresetBase, Operator):
    """Save DXF Export Settings"""
    bl_idname = "dxf_exporter.preset"
    bl_label = "DXF Export Settings"
    preset_menu = DXFEXPORTER_MT_Preset.__name__

    # Variable used for all preset values
    preset_defines = [
        "op  = bpy.context.active_operator"
    ]
    
    # Properties to store in the preset
    preset_values = [ 
        f"op.{k}" 
        for k in DXFEXPORTER_OT_Export.__annotations__.keys()
    ]

    # Where to store the preset
    preset_subdir = DXFEXPORTER_OT_Export.bl_idname


def draw_preset(self, context):
    layout = self.layout    
    
    row = layout.row(align=True)
    row.menu(DXFEXPORTER_MT_Preset.__name__,
             text=DXFEXPORTER_MT_Preset.bl_label)
    row.operator(DXFEXPORTER_OT_Preset.bl_idname, text="", icon='ADD')
    row.operator(DXFEXPORTER_OT_Preset.bl_idname, text="",
                 icon='REMOVE').remove_active = True


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
