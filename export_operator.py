import bpy

from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    FloatProperty, StringProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
)
from bpy.types import Operator

from .export_dxf import DXFExporter
from .shared_properties import (
    dxf_face_type,
    dxf_line_type,
    dxf_point_type,
    entity_layer,
    entity_color,
)


def update_export_scale(self, context):
    if not self.uniform_export_scale:
        return
    if self.export_scale[0] != self.export_scale[1]:
        self.export_scale[1] = self.export_scale[0]
        return
    if self.export_scale[0] != self.export_scale[2]:
        self.export_scale[2] = self.export_scale[0]


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

    only_selected: BoolProperty(
        name="Export Only Selected Objects",
        default=True,
        description="What object will be exported? Only selected / All objects")

    use_blocks: BoolProperty(
        name="Objects with shared mesh as Blocks",
        description="If objects share the same mesh data, they will be exported as Block objects.\nWarning : Will not work if linked objects have a rotation along X or Y",
        default=False,
    )

    faces_export: EnumProperty(
        name="Export Faces",
        default=dxf_face_type.MESH.value,
        items=[(f_t.value,)*3 for f_t in dxf_face_type])

    lines_export: EnumProperty(
        name="Export Lines",
        default=dxf_line_type.NONE.value,
        items=[(l_t.value,)*3 for l_t in dxf_line_type])

    points_export: EnumProperty(
        name="Export Points",
        default=dxf_point_type.NONE.value,
        items=[(p_t.value,)*3 for p_t in dxf_point_type])

    entity_layer_to: EnumProperty(
        name="Object Layer",
        default=entity_layer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,)*3 for e_l in entity_layer])

    entity_layer_separate: BoolProperty(
        name="Face, Edge and Vertex Sub-Layers",
        description="Faces, lines and points are drawn on separate sub-layers",
        # TODO : Add customization in addonprefs
        default=False,
    )
    
    entity_layer_color: BoolProperty(
        name="Use Color",
        description="Set layer color if available in source",
        default=True,
    )
    
    entity_layer_transparency: BoolProperty(
        name="Use Transparency",
        description="Set layer transparency if available in source Color",
        default=False,
    )

    entity_color_to: EnumProperty(
        name="Object Color",
        default=entity_color.BYLAYER.value,
        description="Entity COLOR assigned to ?",
        items=[(e_c.value,)*3 for e_c in entity_color])

    entity_color_transparency: BoolProperty(
        name="Use Transparency",
        description="Enable to set color transparency if available in source Color",
        default=False,
    )

    delta_xyz: FloatVectorProperty(
        name="Delta XYZ",
        description="Every entity will be translated by this value in real world",
        default=(0, 0, 0),
        subtype='COORDINATES',
        # unit='LENGTH',
        # size=3,
    )

    uniform_export_scale: BoolProperty(
        name="Uniform Scale",
        description="Scale uniformly in all axes",
        default=True,
        update=update_export_scale,
    )

    export_scale: FloatVectorProperty(
        name="Unit Scale",
        description="This parameter will scale every entity globally, starting at the center of the world (0, 0, 0)",
        default=(1, 1, 1),
        update=update_export_scale,
    )

    verbose: BoolProperty(
        name="Verbose",
        default=False,
        description="Run the exporter in debug mode.  Check the console for output")

    def execute(self, context):
        exporter = DXFExporter(
            debug_mode=self.verbose,
        )
        if not exporter.can_write_file(self.filepath):
            self.report(
                {'ERROR'}, f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software)")
            return {'FINISHED'}
        exporter.write_objects(
            objects=context.selected_objects if self.only_selected else context.scene.objects,
            context=context,
            settings=self,
        )

        if exporter.export_file(self.filepath):
            self.report({'INFO'}, "Export Succesfully Completed")
        else:
            self.report(
                {'ERROR'}, f"Permission Error : File {self.filepath} can't be modified (Close the file in your CAD software and check if you have write permission)")
        if self.verbose:
            for line in exporter.log:
                print(line)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "only_selected")
        layout.label(text="Export Geometry")
        geometry_box = layout.box()
        for prop, name in zip(
                ("faces_export", "lines_export", "points_export"),
                ("Faces", "Edges", "Vertices")
        ):
            geom_split = geometry_box.split(factor=0.3)
            geom_split.label(text=name)
            geom_split.prop(self, prop, text="")
        geometry_box.prop(self, "use_blocks", toggle=True)

        layout.label(text="Object Layer")
        layer_box = layout.box()
        layer_box.prop(self, "entity_layer_to", text="")
        layer_box.prop(self, "entity_layer_separate", toggle=True)
        layer_color_split = layer_box.split(factor=0.5)
        layer_color_split.prop(self, "entity_layer_color", toggle=True)
        layer_transparency = layer_color_split.row()
        layer_transparency.prop(self, "entity_layer_transparency", toggle=True)
        layer_transparency.enabled = self.entity_layer_color and self.entity_layer_to in (entity_layer.OBJECT_NAME.value, entity_layer.MATERIAL.value)
        
        layout.label(text="Object Color")
        color_box = layout.box()
        color_box.prop(self, "entity_color_to", text="")
        col_transparency = color_box.row()
        col_transparency.prop(self, "entity_color_transparency", toggle=True)
        col_transparency.enabled = self.entity_color_to in (entity_color.OBJECT.value, entity_color.MATERIAL.value)

        layout.label(text="Scale")
        scale_box = layout.box()
        scale_box.prop(self, "uniform_export_scale")
        scale_box.prop(self, "export_scale", index=0, text="X")
        scale_box_y = scale_box.row()
        scale_box_y.prop(self, "export_scale", index=1, text="Y")
        scale_box_y.enabled = not self.uniform_export_scale
        scale_box_z  = scale_box.row()
        scale_box_z.prop(self, "export_scale", index=2, text="Z")
        scale_box_z.enabled = not self.uniform_export_scale

        layout.label(text="Delta XYZ")
        delta_xyz_box = layout.box()
        delta_xyz_box.prop(self, "delta_xyz", index=0, text="X")
        delta_xyz_box.prop(self, "delta_xyz", index=1, text="Y")
        delta_xyz_box.prop(self, "delta_xyz", index=2, text="Z")

        layout.prop(self, "verbose")


def menu_func_export(self, context):
    self.layout.operator(DXFExporter_OT_Export.bl_idname,
                         text="Drawing Interchange File (.dxf)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
