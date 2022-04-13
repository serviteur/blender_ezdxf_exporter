def draw(self, layout):
    layout.label(text="Scale")
    scale_box = layout.box()
    scale_box.prop(self, "uniform_export_scale", toggle=True)
    scale_row = scale_box.row(align=True)
    scale_row.prop(self, "export_scale", index=0, text="X")
    scale_box_y = scale_row.row()
    scale_box_y.prop(self, "export_scale", index=1, text="Y")
    scale_box_y.enabled = not self.uniform_export_scale
    scale_box_z = scale_row.row()
    scale_box_z.prop(self, "export_scale", index=2, text="Z")
    scale_box_z.enabled = not self.uniform_export_scale

    layout.label(text="Coordinate System")
    layout.prop(self.ucs, "type")
    if self.ucs.type == "CAMERA":
        row = layout.row(align=True)
        row.prop(self.ucs, "camera_type", text="")
        if self.ucs.camera_type == "CUSTOM":
            row.prop(self.ucs, "camera_custom", text="")

    layout.label(text="Delta XYZ")
    col = layout.box().column(align=True)
    col.prop(self, "delta_xyz", index=0, text="X")
    col.prop(self, "delta_xyz", index=1, text="Y")
    col.prop(self, "delta_xyz", index=2, text="Z")
