from enum import Enum
import os
from os import listdir
from os.path import isfile, join, splitext

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

from .__init__ import NO_EXPORT
from .color_settings import ACIColor
from ..shared_maths import get_256_rgb_a


class TextType(Enum):
    NONE = NO_EXPORT
    MTEXT = "MText"
    TEXT = "Text"
    MESH = "Mesh"


class FillColor(Enum):
    NONE = "No Fill"
    CUSTOM = "Custom Color"
    ACI = "Autocad Color"
    BACKGROUND = "Background Color"


FONTS_TTF = (
    [
        (f, splitext(f)[0].capitalize(), "")
        for f in listdir("C:/Windows/Fonts")
        if isfile(join("C:/Windows/Fonts", f))
        if splitext(f)[1] == ".ttf"
    ]
    if os.name == "nt"
    else []
)  # TODO : support override fonts for Linux and OSx


class TextSettings(PropertyGroup):
    fill_type: EnumProperty(name="Fill", default=FillColor.NONE.value, items=[(f_c.value,) * 3 for f_c in FillColor])
    fill_color_rgb: FloatVectorProperty(name="Fill Color", default=(1, 1, 1), min=0, max=1, subtype="COLOR")
    fill_color_aci: EnumProperty(
        name="Fill Color",
        description="Autocad Color Index - Color as an integer [0:255]",
        default=ACIColor.WHITE.value[0],
        items=[aci.value for aci in ACIColor],
    )
    fill_scale: FloatProperty(
        name="Fill Scale", description="1=Exact Fit, 1.5 = default, 5=Max", default=1.5, min=1, max=5
    )
    font_name: EnumProperty(
        name="Font",
        description="Default font to use (Bfont is automatically set to this)",
        items=FONTS_TTF,
    )
    font_override: BoolProperty(
        name="Override Font",
        description="Override Font on all Text objects (Bfont is automatically overriden)",
        default=False,
    )

    def get_color_value(self):
        if self.fill_type == FillColor.CUSTOM.value:
            return tuple(get_256_rgb_a(self.fill_color_rgb)[0])
        elif self.fill_type == FillColor.ACI.value:
            return int(self.fill_color_aci)
        elif self.fill_type == FillColor.BACKGROUND.value:
            return "canvas"
        return None

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
