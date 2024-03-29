import bpy


class DXFEXPORTER_MT_Preset(bpy.types.Menu):
    bl_label = "DXF Export"
    preset_subdir = "dxf_exporter.export"
    preset_operator = "script.execute_preset"

    def draw(self, context):
        self.draw_preset(context)


def draw_op(self, context):
    layout = self.layout
    draw_preset(self, context)
    self.settings.draw(layout, context)
    layout.prop(self, "verbose")


def draw_preset(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(DXFEXPORTER_MT_Preset.__name__, text=DXFEXPORTER_MT_Preset.bl_label)
    row.operator("dxf_exporter.preset", text="", icon="ADD")
    row.operator("dxf_exporter.preset", text="", icon="REMOVE").remove_active = True


def menu_func_export(self, context):
    self.layout.operator("dxf_exporter.export", text="Drawing Interchange File (.dxf)")


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
