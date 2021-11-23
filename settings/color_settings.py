from enum import Enum
from bpy.types import (
    PropertyGroup,
)
from bpy.props import EnumProperty, BoolProperty, FloatVectorProperty, IntProperty


__ACI_RGB_MAPPING = (
    (0, 0, 0),
    (1.0, 0.0, 0.0),
    (1.0, 1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 1.0),
    (0.0, 0.0, 1.0),
    (1.0, 0.0, 1.0),
    (1.0, 1.0, 1.0),
    (0.2549019607843137, 0.2549019607843137, 0.2549019607843137),
    (0.5019607843137255, 0.5019607843137255, 0.5019607843137255),
    (1.0, 0.0, 0.0),
    (1.0, 0.6666666666666666, 0.6666666666666666),
    (0.7411764705882353, 0.0, 0.0),
    (0.7411764705882353, 0.49411764705882355, 0.49411764705882355),
    (0.5058823529411764, 0.0, 0.0),
    (0.5058823529411764, 0.33725490196078434, 0.33725490196078434),
    (0.40784313725490196, 0.0, 0.0),
    (0.40784313725490196, 0.27058823529411763, 0.27058823529411763),
    (0.30980392156862746, 0.0, 0.0),
    (0.30980392156862746, 0.20784313725490197, 0.20784313725490197),
    (1.0, 0.24705882352941178, 0.0),
    (1.0, 0.7490196078431373, 0.6666666666666666),
    (0.7411764705882353, 0.1803921568627451, 0.0),
    (0.7411764705882353, 0.5529411764705883, 0.49411764705882355),
    (0.5058823529411764, 0.12156862745098039, 0.0),
    (0.5058823529411764, 0.3764705882352941, 0.33725490196078434),
    (0.40784313725490196, 0.09803921568627451, 0.0),
    (0.40784313725490196, 0.3058823529411765, 0.27058823529411763),
    (0.30980392156862746, 0.07450980392156863, 0.0),
    (0.30980392156862746, 0.23137254901960785, 0.20784313725490197),
    (1.0, 0.4980392156862745, 0.0),
    (1.0, 0.8313725490196079, 0.6666666666666666),
    (0.7411764705882353, 0.3686274509803922, 0.0),
    (0.7411764705882353, 0.615686274509804, 0.49411764705882355),
    (0.5058823529411764, 0.25098039215686274, 0.0),
    (0.5058823529411764, 0.4196078431372549, 0.33725490196078434),
    (0.40784313725490196, 0.20392156862745098, 0.0),
    (0.40784313725490196, 0.33725490196078434, 0.27058823529411763),
    (0.30980392156862746, 0.15294117647058825, 0.0),
    (0.30980392156862746, 0.25882352941176473, 0.20784313725490197),
    (1.0, 0.7490196078431373, 0.0),
    (1.0, 0.9176470588235294, 0.6666666666666666),
    (0.7411764705882353, 0.5529411764705883, 0.0),
    (0.7411764705882353, 0.6784313725490196, 0.49411764705882355),
    (0.5058823529411764, 0.3764705882352941, 0.0),
    (0.5058823529411764, 0.4627450980392157, 0.33725490196078434),
    (0.40784313725490196, 0.3058823529411765, 0.0),
    (0.40784313725490196, 0.37254901960784315, 0.27058823529411763),
    (0.30980392156862746, 0.23137254901960785, 0.0),
    (0.30980392156862746, 0.28627450980392155, 0.20784313725490197),
    (1.0, 1.0, 0.0),
    (1.0, 1.0, 0.6666666666666666),
    (0.7411764705882353, 0.7411764705882353, 0.0),
    (0.7411764705882353, 0.7411764705882353, 0.49411764705882355),
    (0.5058823529411764, 0.5058823529411764, 0.0),
    (0.5058823529411764, 0.5058823529411764, 0.33725490196078434),
    (0.40784313725490196, 0.40784313725490196, 0.0),
    (0.40784313725490196, 0.40784313725490196, 0.27058823529411763),
    (0.30980392156862746, 0.30980392156862746, 0.0),
    (0.30980392156862746, 0.30980392156862746, 0.20784313725490197),
    (0.7490196078431373, 1.0, 0.0),
    (0.9176470588235294, 1.0, 0.6666666666666666),
    (0.5529411764705883, 0.7411764705882353, 0.0),
    (0.6784313725490196, 0.7411764705882353, 0.49411764705882355),
    (0.3764705882352941, 0.5058823529411764, 0.0),
    (0.4627450980392157, 0.5058823529411764, 0.33725490196078434),
    (0.3058823529411765, 0.40784313725490196, 0.0),
    (0.37254901960784315, 0.40784313725490196, 0.27058823529411763),
    (0.23137254901960785, 0.30980392156862746, 0.0),
    (0.28627450980392155, 0.30980392156862746, 0.20784313725490197),
    (0.4980392156862745, 1.0, 0.0),
    (0.8313725490196079, 1.0, 0.6666666666666666),
    (0.3686274509803922, 0.7411764705882353, 0.0),
    (0.615686274509804, 0.7411764705882353, 0.49411764705882355),
    (0.25098039215686274, 0.5058823529411764, 0.0),
    (0.4196078431372549, 0.5058823529411764, 0.33725490196078434),
    (0.20392156862745098, 0.40784313725490196, 0.0),
    (0.33725490196078434, 0.40784313725490196, 0.27058823529411763),
    (0.15294117647058825, 0.30980392156862746, 0.0),
    (0.25882352941176473, 0.30980392156862746, 0.20784313725490197),
    (0.24705882352941178, 1.0, 0.0),
    (0.7490196078431373, 1.0, 0.6666666666666666),
    (0.1803921568627451, 0.7411764705882353, 0.0),
    (0.5529411764705883, 0.7411764705882353, 0.49411764705882355),
    (0.12156862745098039, 0.5058823529411764, 0.0),
    (0.3764705882352941, 0.5058823529411764, 0.33725490196078434),
    (0.09803921568627451, 0.40784313725490196, 0.0),
    (0.3058823529411765, 0.40784313725490196, 0.27058823529411763),
    (0.07450980392156863, 0.30980392156862746, 0.0),
    (0.23137254901960785, 0.30980392156862746, 0.20784313725490197),
    (0.0, 1.0, 0.0),
    (0.6666666666666666, 1.0, 0.6666666666666666),
    (0.0, 0.7411764705882353, 0.0),
    (0.49411764705882355, 0.7411764705882353, 0.49411764705882355),
    (0.0, 0.5058823529411764, 0.0),
    (0.33725490196078434, 0.5058823529411764, 0.33725490196078434),
    (0.0, 0.40784313725490196, 0.0),
    (0.27058823529411763, 0.40784313725490196, 0.27058823529411763),
    (0.0, 0.30980392156862746, 0.0),
    (0.20784313725490197, 0.30980392156862746, 0.20784313725490197),
    (0.0, 1.0, 0.24705882352941178),
    (0.6666666666666666, 1.0, 0.7490196078431373),
    (0.0, 0.7411764705882353, 0.1803921568627451),
    (0.49411764705882355, 0.7411764705882353, 0.5529411764705883),
    (0.0, 0.5058823529411764, 0.12156862745098039),
    (0.33725490196078434, 0.5058823529411764, 0.3764705882352941),
    (0.0, 0.40784313725490196, 0.09803921568627451),
    (0.27058823529411763, 0.40784313725490196, 0.3058823529411765),
    (0.0, 0.30980392156862746, 0.07450980392156863),
    (0.20784313725490197, 0.30980392156862746, 0.23137254901960785),
    (0.0, 1.0, 0.4980392156862745),
    (0.6666666666666666, 1.0, 0.8313725490196079),
    (0.0, 0.7411764705882353, 0.3686274509803922),
    (0.49411764705882355, 0.7411764705882353, 0.615686274509804),
    (0.0, 0.5058823529411764, 0.25098039215686274),
    (0.33725490196078434, 0.5058823529411764, 0.4196078431372549),
    (0.0, 0.40784313725490196, 0.20392156862745098),
    (0.27058823529411763, 0.40784313725490196, 0.33725490196078434),
    (0.0, 0.30980392156862746, 0.15294117647058825),
    (0.20784313725490197, 0.30980392156862746, 0.25882352941176473),
    (0.0, 1.0, 0.7490196078431373),
    (0.6666666666666666, 1.0, 0.9176470588235294),
    (0.0, 0.7411764705882353, 0.5529411764705883),
    (0.49411764705882355, 0.7411764705882353, 0.6784313725490196),
    (0.0, 0.5058823529411764, 0.3764705882352941),
    (0.33725490196078434, 0.5058823529411764, 0.4627450980392157),
    (0.0, 0.40784313725490196, 0.3058823529411765),
    (0.27058823529411763, 0.40784313725490196, 0.37254901960784315),
    (0.0, 0.30980392156862746, 0.23137254901960785),
    (0.20784313725490197, 0.30980392156862746, 0.28627450980392155),
    (0.0, 1.0, 1.0),
    (0.6666666666666666, 1.0, 1.0),
    (0.0, 0.7411764705882353, 0.7411764705882353),
    (0.49411764705882355, 0.7411764705882353, 0.7411764705882353),
    (0.0, 0.5058823529411764, 0.5058823529411764),
    (0.33725490196078434, 0.5058823529411764, 0.5058823529411764),
    (0.0, 0.40784313725490196, 0.40784313725490196),
    (0.27058823529411763, 0.40784313725490196, 0.40784313725490196),
    (0.0, 0.30980392156862746, 0.30980392156862746),
    (0.20784313725490197, 0.30980392156862746, 0.30980392156862746),
    (0.0, 0.7490196078431373, 1.0),
    (0.6666666666666666, 0.9176470588235294, 1.0),
    (0.0, 0.5529411764705883, 0.7411764705882353),
    (0.49411764705882355, 0.6784313725490196, 0.7411764705882353),
    (0.0, 0.3764705882352941, 0.5058823529411764),
    (0.33725490196078434, 0.4627450980392157, 0.5058823529411764),
    (0.0, 0.3058823529411765, 0.40784313725490196),
    (0.27058823529411763, 0.37254901960784315, 0.40784313725490196),
    (0.0, 0.23137254901960785, 0.30980392156862746),
    (0.20784313725490197, 0.28627450980392155, 0.30980392156862746),
    (0.0, 0.4980392156862745, 1.0),
    (0.6666666666666666, 0.8313725490196079, 1.0),
    (0.0, 0.3686274509803922, 0.7411764705882353),
    (0.49411764705882355, 0.615686274509804, 0.7411764705882353),
    (0.0, 0.25098039215686274, 0.5058823529411764),
    (0.33725490196078434, 0.4196078431372549, 0.5058823529411764),
    (0.0, 0.20392156862745098, 0.40784313725490196),
    (0.27058823529411763, 0.33725490196078434, 0.40784313725490196),
    (0.0, 0.15294117647058825, 0.30980392156862746),
    (0.20784313725490197, 0.25882352941176473, 0.30980392156862746),
    (0.0, 0.24705882352941178, 1.0),
    (0.6666666666666666, 0.7490196078431373, 1.0),
    (0.0, 0.1803921568627451, 0.7411764705882353),
    (0.49411764705882355, 0.5529411764705883, 0.7411764705882353),
    (0.0, 0.12156862745098039, 0.5058823529411764),
    (0.33725490196078434, 0.3764705882352941, 0.5058823529411764),
    (0.0, 0.09803921568627451, 0.40784313725490196),
    (0.27058823529411763, 0.3058823529411765, 0.40784313725490196),
    (0.0, 0.07450980392156863, 0.30980392156862746),
    (0.20784313725490197, 0.23137254901960785, 0.30980392156862746),
    (0.0, 0.0, 1.0),
    (0.6666666666666666, 0.6666666666666666, 1.0),
    (0.0, 0.0, 0.7411764705882353),
    (0.49411764705882355, 0.49411764705882355, 0.7411764705882353),
    (0.0, 0.0, 0.5058823529411764),
    (0.33725490196078434, 0.33725490196078434, 0.5058823529411764),
    (0.0, 0.0, 0.40784313725490196),
    (0.27058823529411763, 0.27058823529411763, 0.40784313725490196),
    (0.0, 0.0, 0.30980392156862746),
    (0.20784313725490197, 0.20784313725490197, 0.30980392156862746),
    (0.24705882352941178, 0.0, 1.0),
    (0.7490196078431373, 0.6666666666666666, 1.0),
    (0.1803921568627451, 0.0, 0.7411764705882353),
    (0.5529411764705883, 0.49411764705882355, 0.7411764705882353),
    (0.12156862745098039, 0.0, 0.5058823529411764),
    (0.3764705882352941, 0.33725490196078434, 0.5058823529411764),
    (0.09803921568627451, 0.0, 0.40784313725490196),
    (0.3058823529411765, 0.27058823529411763, 0.40784313725490196),
    (0.07450980392156863, 0.0, 0.30980392156862746),
    (0.23137254901960785, 0.20784313725490197, 0.30980392156862746),
    (0.4980392156862745, 0.0, 1.0),
    (0.8313725490196079, 0.6666666666666666, 1.0),
    (0.3686274509803922, 0.0, 0.7411764705882353),
    (0.615686274509804, 0.49411764705882355, 0.7411764705882353),
    (0.25098039215686274, 0.0, 0.5058823529411764),
    (0.4196078431372549, 0.33725490196078434, 0.5058823529411764),
    (0.20392156862745098, 0.0, 0.40784313725490196),
    (0.33725490196078434, 0.27058823529411763, 0.40784313725490196),
    (0.15294117647058825, 0.0, 0.30980392156862746),
    (0.25882352941176473, 0.20784313725490197, 0.30980392156862746),
    (0.7490196078431373, 0.0, 1.0),
    (0.9176470588235294, 0.6666666666666666, 1.0),
    (0.5529411764705883, 0.0, 0.7411764705882353),
    (0.6784313725490196, 0.49411764705882355, 0.7411764705882353),
    (0.3764705882352941, 0.0, 0.5058823529411764),
    (0.4627450980392157, 0.33725490196078434, 0.5058823529411764),
    (0.3058823529411765, 0.0, 0.40784313725490196),
    (0.37254901960784315, 0.27058823529411763, 0.40784313725490196),
    (0.23137254901960785, 0.0, 0.30980392156862746),
    (0.28627450980392155, 0.20784313725490197, 0.30980392156862746),
    (1.0, 0.0, 1.0),
    (1.0, 0.6666666666666666, 1.0),
    (0.7411764705882353, 0.0, 0.7411764705882353),
    (0.7411764705882353, 0.49411764705882355, 0.7411764705882353),
    (0.5058823529411764, 0.0, 0.5058823529411764),
    (0.5058823529411764, 0.33725490196078434, 0.5058823529411764),
    (0.40784313725490196, 0.0, 0.40784313725490196),
    (0.40784313725490196, 0.27058823529411763, 0.40784313725490196),
    (0.30980392156862746, 0.0, 0.30980392156862746),
    (0.30980392156862746, 0.20784313725490197, 0.30980392156862746),
    (1.0, 0.0, 0.7490196078431373),
    (1.0, 0.6666666666666666, 0.9176470588235294),
    (0.7411764705882353, 0.0, 0.5529411764705883),
    (0.7411764705882353, 0.49411764705882355, 0.6784313725490196),
    (0.5058823529411764, 0.0, 0.3764705882352941),
    (0.5058823529411764, 0.33725490196078434, 0.4627450980392157),
    (0.40784313725490196, 0.0, 0.3058823529411765),
    (0.40784313725490196, 0.27058823529411763, 0.37254901960784315),
    (0.30980392156862746, 0.0, 0.23137254901960785),
    (0.30980392156862746, 0.20784313725490197, 0.28627450980392155),
    (1.0, 0.0, 0.4980392156862745),
    (1.0, 0.6666666666666666, 0.8313725490196079),
    (0.7411764705882353, 0.0, 0.3686274509803922),
    (0.7411764705882353, 0.49411764705882355, 0.615686274509804),
    (0.5058823529411764, 0.0, 0.25098039215686274),
    (0.5058823529411764, 0.33725490196078434, 0.4196078431372549),
    (0.40784313725490196, 0.0, 0.20392156862745098),
    (0.40784313725490196, 0.27058823529411763, 0.33725490196078434),
    (0.30980392156862746, 0.0, 0.15294117647058825),
    (0.30980392156862746, 0.20784313725490197, 0.25882352941176473),
    (1.0, 0.0, 0.24705882352941178),
    (1.0, 0.6666666666666666, 0.7490196078431373),
    (0.7411764705882353, 0.0, 0.1803921568627451),
    (0.7411764705882353, 0.49411764705882355, 0.5529411764705883),
    (0.5058823529411764, 0.0, 0.12156862745098039),
    (0.5058823529411764, 0.33725490196078434, 0.3764705882352941),
    (0.40784313725490196, 0.0, 0.09803921568627451),
    (0.40784313725490196, 0.27058823529411763, 0.3058823529411765),
    (0.30980392156862746, 0.0, 0.07450980392156863),
    (0.30980392156862746, 0.20784313725490197, 0.23137254901960785),
    (0.2, 0.2, 0.2),
    (0.3137254901960784, 0.3137254901960784, 0.3137254901960784),
    (0.4117647058823529, 0.4117647058823529, 0.4117647058823529),
    (0.5098039215686274, 0.5098039215686274, 0.5098039215686274),
    (0.7450980392156863, 0.7450980392156863, 0.7450980392156863),
    (1.0, 1.0, 1.0),
)


class ACIColor(Enum):
    BLACK = ("0", "Black", "0")
    RED = ("1", "Red", "1")
    YELLOW = ("2", "Yellow", "2")
    GREEN = ("3", "Green", "3")
    CYAN = ("4", "Cyan", "4")
    BLUE = ("5", "Blue", "5")
    MAGENTA = ("6", "Magenta", "6")
    WHITE = ("7", "White", "Default Value (7)")


class EntityColor(Enum):
    BYLAYER = "BYLAYER"
    BYBLOCK = "BYBLOCK"
    OBJECT = "Object Color"
    MATERIAL = "Material Color"
    COLLECTION = "Collection Tag Color"
    ACI = "Autocad Color Index (ACI)"
    CUSTOM = "Custom Color"


def source_has_alpha(source: EntityColor):
    return source in (
        EntityColor.OBJECT.value,
        EntityColor.MATERIAL.value,
        EntityColor.CUSTOM.value,
    )


class ColorSettings(PropertyGroup):
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
        default=ACIColor.WHITE.value[0],
        items=[aci.value for aci in ACIColor],
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
        if obj_name is None:
            obj_name = "Default Object"
        layout.label(text=obj_name + " Color")
        color_box = layout.box()
        color_box.prop(self, "entity_color_to", text="")
        if self.entity_color_to == EntityColor.ACI.value:
            row = color_box.row()
            row.prop(self, "entity_color_aci")
        elif self.entity_color_to == EntityColor.CUSTOM.value:
            row = color_box.row()
            row.prop(self, "entity_color_custom")
        col = color_box.column(align=False, heading="Transparency")
        col.use_property_decorate = False
        col.use_property_split = True
        row = col.row(align=True)
        sub = row.row(align=True)
        sub.prop(self, "entity_color_use_transparency", text="")
        sub = sub.row(align=True)
        link = sub.row()
        link.prop(
            self,
            "entity_color_transparency_link",
            text="",
            icon="LINKED" if self.entity_color_transparency_link else "UNLINKED",
        )
        link.active = source_has_alpha(self.entity_color_to)
        val = sub.row()
        val.prop(self, "entity_color_transparency", text="")
        val.active = not self.entity_color_transparency_link or not link.active
        sub.active = self.entity_color_use_transparency
