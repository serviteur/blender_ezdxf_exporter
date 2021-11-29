import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
)

from ezdxf_exporter.data.color.constants import ACIColor
from ezdxf_exporter.core.shared_maths import get_256_rgb_a
from .constants import FillColor, FONTS_TTF
from .ui import draw



class TextSettings(bpy.types.PropertyGroup):
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
        draw(self, layout)
