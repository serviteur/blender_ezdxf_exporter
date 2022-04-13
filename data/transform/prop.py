from bpy.types import PropertyGroup
from bpy.props import (
    FloatVectorProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,
)
from ezdxf_exporter.data.camera.helper import get_all_camera_names
from .helper import update_export_scale
from .ui import draw
from .constants import UCS, UCS_DESCRIPTIONS


class UCSSettings(PropertyGroup):
    type: EnumProperty(
        name="UCS",
        description="User Coordinate System",
        items=((ucs_item.value, ucs_item.value.title(), UCS_DESCRIPTIONS.get(ucs_item.value, "")) for ucs_item in UCS),
    )

    camera_type: EnumProperty(
        name="Chosen Camera",
        items=(
            ("ACTIVE",) * 3,
            ("CUSTOM",) * 3,
        ),
    )
    camera_custom: EnumProperty(
        name="Custom Camera", items=lambda self, context: [(n,) * 3 for n in get_all_camera_names(context)]
    )


class TransformSettings(PropertyGroup):
    delta_xyz: FloatVectorProperty(
        name="Delta XYZ",
        description="Every entity will be translated by this value in real world",
        default=(0, 0, 0),
        subtype="COORDINATES",
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

    ucs: PointerProperty(type=UCSSettings)

    def draw(self, layout):
        draw(self, layout)
