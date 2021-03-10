from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
)
from ..shared_properties import (
    dxf_face_type,
    dxf_line_type,
    dxf_point_type,
    text_type,
)


class GeometrySettings(PropertyGroup):
    faces_export: EnumProperty(
        name="Export Faces",
        default=dxf_face_type.MESH.value,
        items=[(f_t.value,)*3 for f_t in dxf_face_type])

    lines_export: EnumProperty(
        name="Export Lines",
        default=dxf_line_type.NONE.value,
        items=[(l_t.value,)*3 for l_t in dxf_line_type])

    points_export: EnumProperty(
        name="Export Points",
        default=dxf_point_type.NONE.value,
        items=[(p_t.value,)*3 for p_t in dxf_point_type])

    texts_export: EnumProperty(
        name="Export Texts",
        default=text_type.MTEXT.value,
        items=[(t_t.value,)*3 for t_t in text_type])

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities",
        default=True,
    )

    def draw(self, layout):
        layout.label(text="Export Geometry")
        geometry_box = layout.box()
        for prop, name in zip(
                (
                    "faces_export", 
                    "lines_export", 
                    "points_export",
                    "texts_export",
                ),
                (
                    "Faces", 
                    "Edges", 
                    "Vertices",
                    "Texts",
                )
        ):
            geom_split = geometry_box.split(factor=0.3, align=True)
            geom_split.label(text=name)
            geom_split.prop(self, prop, text="")
        geometry_box.prop(self, "use_blocks", toggle=True)
