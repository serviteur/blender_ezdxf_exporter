from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
)

class dxf_face_type(Enum):
    NONE = 'No Export'
    MESH = 'MESH'
    FACES3D = '3DFACEs'
    POLYFACE = 'POLYFACE'


class dxf_line_type(Enum):
    NONE = 'No Export'
    LINES = 'LINEs'
    POLYLINES = 'POLYLINEs'


class dxf_point_type(Enum):
    NONE = 'No Export'
    POINTS = 'POINTs'


class text_type(Enum):
    MTEXT = 'MText'
    TEXT = 'Text'
    MESH = 'Mesh'


class camera_type(Enum):
    NONE = 'No Export'
    VIEWPORT = 'VIEWPORT (Paperspace)'
    VPORT = 'VPORT (Modelspace)'
    VIEW = 'VIEW (Modelspace)'


class DataSettings(PropertyGroup):
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

    
    cameras_export: EnumProperty(
        name="Export Cameras",
        default=camera_type.VIEWPORT.value,
        items=[(c_t.value,)*3 for c_t in camera_type])

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities",
        default=True,
    )

    def draw(self, layout, objects):
        layout.label(text="Export Data")
        geometry_box = layout.box()
        lookup_type_dic = {}
        for obj in objects:
            lookup_type_dic[obj.type] = True
        for prop, name, _type in zip(
                (
                    "faces_export", 
                    "lines_export", 
                    "points_export",
                    "texts_export",
                    "empties_export",
                    "cameras_export",
                ),
                (
                    "Faces", 
                    "Edges", 
                    "Vertices",
                    "Texts",
                    "Empties",
                    "Cameras",
                ),
                (
                    'MESH',
                    'MESH',
                    'MESH',
                    'FONT',
                    'EMPTY',
                    'CAMERA',
                )
        ):
            if lookup_type_dic.get(_type) is None:
                continue
            geom_split = geometry_box.split(factor=0.3, align=True)
            geom_split.label(text=name)
            geom_split.prop(self, prop, text="")
        geometry_box.prop(self, "use_blocks", toggle=True)
