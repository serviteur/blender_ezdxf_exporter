from bpy.types import PropertyGroup
from bpy.props import (
    FloatVectorProperty,
    BoolProperty,
)
from ..settings.layer_settings import EntityLayer


def update_export_scale(self, context):
    if not self.uniform_export_scale:
        return
    if self.export_scale[0] != self.export_scale[1]:
        self.export_scale[1] = self.export_scale[0]
        return
    if self.export_scale[0] != self.export_scale[2]:
        self.export_scale[2] = self.export_scale[0]


class TransformSettings(PropertyGroup):
    delta_xyz: FloatVectorProperty(
        name="Delta XYZ",
        description="Every entity will be translated by this value in real world",
        default=(0, 0, 0),
        subtype='COORDINATES',
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

        layout.label(text="Delta XYZ")
        col = layout.box().column(align=True)
        col.prop(self, "delta_xyz", index=0, text="X")
        col.prop(self, "delta_xyz", index=1, text="Y")
        col.prop(self, "delta_xyz", index=2, text="Z")
