import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .export_dxf import DXFExporter
from .shared_properties import (
    mesh_as_items,
    mesh_types,
    entity_layer_from_items,
)


class DXFExporter_OT_Export(Operator, ExportHelper):
    """File selection operator to export objects in DXF file"""
    bl_idname = "dxf_exporter.export"
    bl_label = "Export As DXF"

    filename_ext = ".dxf"

    only_selected: BoolProperty(
        name="Only Selected", 
        default=True,
        description="What object will be exported? Only selected / All objects")

    apply_modifiers: BoolProperty(
        name="Apply Modifiers", 
        default=True,
        description="Export the objects with all modifiers and shapekeys applied")

    mesh_as: EnumProperty( 
        name="Export Mesh As", 
        default=str(mesh_types.FACES3D),
        description="Select representation of a mesh",
        items=mesh_as_items)

    entitylayer_from: EnumProperty(
        name="Object Layer", 
        default=entity_layer_from_items[1][0],
        description="Entity LAYER assigned to?",
        items=entity_layer_from_items)

    verbose: BoolProperty(
        name="Verbose", 
        default=False,
        description="Run the exporter in debug mode.  Check the console for output")

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

    def execute(self, context):
        exporter = DXFExporter(
            debug_mode=self.verbose,
        )
        exporter.write_objects(
            objects=context.selected_objects if self.only_selected else context.scene.objects,
            context=context,
            apply_modifiers=self.apply_modifiers,
            mesh_as=self.mesh_as,
            layer=self.entitylayer_from)
        exporter.export_file(self.filepath)
        if self.verbose:
            for line in exporter.log:
                print(line)
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(DXFExporter_OT_Export.bl_idname,
                         text="Drawing Interchange File (.dxf)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
