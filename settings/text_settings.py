from enum import Enum

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
    EnumProperty
)

from .__init__ import NO_EXPORT
from .color_settings import ACIColor
from ..shared_maths import get_256_rgb_a


class TextType(Enum):
    NONE = NO_EXPORT
    MTEXT = 'MText'
    TEXT = 'Text'
    MESH = 'Mesh'


class FillColor(Enum):
    NONE = "No Fill"
    CUSTOM = "Custom Color"
    ACI = "Autocad Color"
    BACKGROUND = "Background Color"


class TextSettings(PropertyGroup):
    fill_type: EnumProperty(
        name="Fill",
        default=FillColor.NONE.value,
        items=[(f_c.value,)*3 for f_c in FillColor])
    fill_color_rgb: FloatVectorProperty(
        name="Fill Color", default=(1, 1, 1), min=0, max=1, subtype='COLOR')
    fill_color_aci: EnumProperty(
        name="Fill Color",
        description="Autocad Color Index - Color as an integer [0:255]",
        default=ACIColor.WHITE.value[0],
        items=[aci.value for aci in ACIColor],
    )
    fill_scale: FloatProperty(
        name="Fill Scale",
        description="1=Exact Fit, 1.5 = default, 5=Max",
        default=1.5, 
        min=1, 
        max=5)

    def get_color_value(self):
        if self.fill_type == FillColor.CUSTOM.value:
            return tuple(get_256_rgb_a(self.fill_color_rgb)[0])
        elif self.fill_type == FillColor.ACI.value:
            return int(self.fill_color_aci)
        elif self.fill_type == FillColor.BACKGROUND.value:
            return 'canvas'
        return None


    def draw(self, layout):
        box = layout.box()
        box.prop(self, "fill_type")

        row = box.row()
        if self.fill_type == FillColor.CUSTOM.value:
            row.prop(self, "fill_color_rgb", text="")
        if self.fill_type == FillColor.ACI.value:
            row.prop(self, "fill_color_aci", text="")
        if self.fill_type != FillColor.NONE.value:
            row.prop(self, "fill_scale", text="Scale")
