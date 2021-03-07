import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .export_dxf import DXFExporter
from .shared_properties import (
    dxf_mesh_type,
    entity_layer,
    entity_color,
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

    mesh_as: EnumProperty( 
        name="Export Mesh As", 
        default=dxf_mesh_type.FACES3D.value,
        description="Select representation of a mesh",
        items=[(m_t.value,)*3 for m_t in dxf_mesh_type])

    entity_layer_to: EnumProperty(
        name="Object Layer", 
        default=entity_layer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,)*3 for e_l in entity_layer])    
        
    entity_color_to: EnumProperty(
        name="Object Color", 
        default=entity_color.BYLAYER.value,
        description="Entity COLOR assigned to ?",
        items=[(e_c.value,)*3 for e_c in entity_color])

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
            mesh_as=self.mesh_as,
            color=self.entity_color_to,
            layer=self.entity_layer_to,
            )
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
