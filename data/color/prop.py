from enum import Enum
import bpy
from bpy.props import EnumProperty, BoolProperty, FloatVectorProperty, IntProperty
from .helper import get_aci_colors
from .ui import draw
from .constants import EntityColor


class ColorSettings(bpy.types.PropertyGroup):
    entity_color_to: EnumProperty(
        name="Object Color",
        default=EntityColor.BYLAYER.value,
        description="Entity COLOR assigned to ?",
        items=[(e_c.value,) * 3 for e_c in EntityColor],
    )

    entity_color_use_transparency: BoolProperty(
        name="Use Transparency",
        description="Enable to set color transparency if available in source Color",
        default=False,
    )

    entity_color_transparency_link: BoolProperty(
        name="Link Transparency to source",
        description="Use Alpha value in source color if available",
        default=True,
    )

    entity_color_transparency: IntProperty(
        name="Override Transparency",
        description="Override Transparency on Object",
        default=0,
        min=0,
        max=100,
    )

    entity_color_aci: EnumProperty(
        name="ACI",
        description="Autocad Color Index - Color as an integer [0:255]",
        # default=ACIColor.WHITE.value[0],
        items=get_aci_colors,
    )

    entity_color_custom: FloatVectorProperty(
        name="Custom Color",
        description="Input custom color for object",
        subtype="COLOR",
        size=4,
        min=0,
        max=1,
        default=(1, 1, 1, 1),
    )

    def draw(self, layout, obj_name=None):
        draw(self, layout, obj_name)
