import os
from .constants import FillColor


def draw(self, layout):
    box = layout.box()
    box.label(text="Text Options")
    box.prop(self, "fill_type", text="Fill")

    if self.fill_type != FillColor.NONE.value:
        fill_row = box.row()
        if self.fill_type == FillColor.CUSTOM.value:
            fill_row.prop(self, "fill_color_rgb", text="")
        if self.fill_type == FillColor.ACI.value:
            fill_row.prop(self, "fill_color_aci", text="")
        if self.fill_type != FillColor.NONE.value:
            fill_row.prop(self, "fill_scale", text="Scale")

    if os.name == "nt":  # TODO : support override fonts for Linux and OSx
        font_row = box.split(factor=0.65, align=True)
        font_row.prop(self, "font_name")
        font_row.prop(self, "font_override", text="Override", toggle=True)
    else:
        self.font_override = False
