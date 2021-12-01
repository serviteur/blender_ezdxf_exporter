import os
from .constants import FillColor


def draw(text_data, layout):
    box = layout.box()
    box.label(text="Text Options")
    box.prop(text_data, "fill_type", text="Fill")

    if text_data.fill_type != FillColor.NONE.value:
        fill_row = box.row()
        if text_data.fill_type == FillColor.CUSTOM.value:
            fill_row.prop(text_data, "fill_color_rgb", text="")
        if text_data.fill_type == FillColor.ACI.value:
            fill_row.prop(text_data, "fill_color_aci", text="")
        if text_data.fill_type != FillColor.NONE.value:
            fill_row.prop(text_data, "fill_scale", text="Scale")

    if os.name == "nt":  # TODO : support override fonts for Linux and OSx
        font_row = box.split(factor=0.65, align=True)
        font_row.prop(text_data, "font_name")
        font_row.prop(text_data, "font_override", text="Override", toggle=True)
    else:
        self.font_override = False
