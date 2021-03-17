from enum import Enum
import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
    BoolVectorProperty,
)
from .__init__ import NO_EXPORT


class FaceType(Enum):
    NONE = NO_EXPORT
    MESH = 'MESH'
    FACES3D = '3DFACEs'
    POLYFACE = 'POLYFACE'


class LineType(Enum):
    NONE = NO_EXPORT
    LINES = 'LINEs'
    POLYLINES = 'POLYLINEs'


class PointType(Enum):
    NONE = NO_EXPORT
    POINTS = 'POINTs'


class TextType(Enum):
    NONE = NO_EXPORT
    MTEXT = 'MText'
    TEXT = 'Text'
    MESH = 'Mesh'


class CurveType(Enum):
    NONE = NO_EXPORT
    # SPLINE = 'Spline'
    MESH = 'Mesh'


class EmptyType(Enum):
    NONE = NO_EXPORT
    BLOCK = 'Block'
    POINT = 'POINT'
    # TODO Export Empty as its viewport Geometry ?


class CameraType(Enum):
    NONE = NO_EXPORT
    VIEWPORT = 'VIEWPORT (Paperspace)'
    # VPORT = 'VPORT (Modelspace)'
    # VIEW = 'VIEW (Modelspace)'


class DimensionType(Enum):
    NONE = NO_EXPORT
    DIM = 'DIMENSION'


class DataSettings(PropertyGroup):
    sub_layers_suffixes = {
        FaceType: "FACES",
        LineType: "EDGES",
        PointType: "VERTICES",
        TextType: "TEXTS",
        EmptyType: "EMPTIES",
        CameraType: "VIEW",
        CurveType: "CURVES",
    }

    faces_export: EnumProperty(
        name="Export Faces",
        default=FaceType.MESH.value,
        items=[(f_t.value,)*3 for f_t in FaceType])

    lines_export: EnumProperty(
        name="Export Lines",
        default=LineType.NONE.value,
        items=[(l_t.value,)*3 for l_t in LineType])

    points_export: EnumProperty(
        name="Export Points",
        default=PointType.NONE.value,
        items=[(p_t.value,)*3 for p_t in PointType])
    
    curves_export: EnumProperty(
        name="Export Curves",
        default=CurveType.MESH.value,
        items=[(c_t.value,)*3 for c_t in CurveType])

    texts_export: EnumProperty(
        name="Export Texts",
        default=TextType.MTEXT.value,
        items=[(t_t.value,)*3 for t_t in TextType])

    empties_export: EnumProperty(
        name="Export Empties",
        default=EmptyType.NONE.value,
        items=[(e_t.value,)*3 for e_t in EmptyType])

    cameras_export: EnumProperty(
        name="Export Cameras",
        default=CameraType.VIEWPORT.value,
        items=[(c_t.value,)*3 for c_t in CameraType])
    
    dimensions_export: EnumProperty(
        name="Export Dimensions",
        description="Export Dimensions extracted from the built-in Measure Tool\nWarning : Works only with XY Planar dimensions",
        default=DimensionType.DIM.value,
        items=[(d_t.value,)*3 for d_t in DimensionType])
    
    use_dimensions:BoolProperty(
        name="Export Dimensions",
        default=False,
    )

    entity_link: BoolVectorProperty(
        name="Use Exporter settings",
        description="Use Exporter settings for exported entities if ON, else use default ones",
        size=len(sub_layers_suffixes),
        default=(True,) * len(sub_layers_suffixes)
    )

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities",
        default=True,
    )

    def draw(self, layout, objects):
        layout.label(text="Export Data")
        geometry_box = layout.box()
        col = geometry_box.column(align=True)
        lookup_type_dic = {}
        for obj in objects:
            lookup_type_dic[obj.type] = True
        i = -1
        for prop, name, _types in (
            ("faces_export", "Faces", ('MESH', 'CURVE', 'FONT')),
            ("lines_export", "Edges", ('MESH', 'CURVE', 'FONT')),
            ("points_export", "Vertices", ('MESH', 'CURVE', 'FONT')),
            ("curves_export", "Curves", ('CURVE',)),
            ("texts_export", "Texts", ('FONT',)),
            ("empties_export", "Empties", ('EMPTY',)),
            ("cameras_export", "Cameras", ('CAMERA',)),
        ):
            i += 1
            mesh_type_supported = False
            for _type in _types:
                if lookup_type_dic.get(_type) is not None:
                    mesh_type_supported = True
                    break
            if not mesh_type_supported:
                continue
            geom_split = col.split(factor=0.3, align=True)
            geom_split.label(text=name)
            geom_split = geom_split.split(factor=0.9, align=True)
            geom_split.prop(self, prop, text="")
            link = geom_split.row(align=True)
            link.prop(self, "entity_link", index=i, text="",
                      icon='LINKED' if self.entity_link[i] else 'UNLINKED')
            # NONE.value is the same for all entity enums
            link.active = getattr(self, prop) != TextType.NONE.value
        
        self.use_dimensions = 'Annotations' in bpy.data.grease_pencils and 'RulerData3D' in bpy.data.grease_pencils[
            "Annotations"].layers
        if self.use_dimensions:
            dim_row = col.split(factor= 0.3, align=True)
            dim_row.label(text="Measures")
            dim_row.prop(self, "dimensions_export", text="")
        
        geometry_box.prop(self, "use_blocks")

    def get_sub_layer_suffix(self, entity_type):
        # TODO : Add customization in addonprefs
        suffix = self.sub_layers_suffixes.get(entity_type, "")
        return suffix if suffix == "" else ("_" + suffix)