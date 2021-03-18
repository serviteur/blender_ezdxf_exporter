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
        DimensionType: "DIMENSIONS",
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

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities",
        default=True,
    )

    def draw(self, layout, objects, entities_properties):
        layout.label(text="Export Data")
        geometry_box = layout.box()
        col = geometry_box.column(align=True)
        lookup_type_dic = {}
        for obj in objects:
            lookup_type_dic[obj.type] = True
        entities_settings_dic = {}
        for entity_settings in entities_properties:
            entities_settings_dic[entity_settings.id] = entity_settings
        i = -1
        for prop, name, _types, entity_type in (
            ("faces_export", "Faces", ('MESH', 'CURVE', 'FONT'), FaceType),
            ("lines_export", "Edges", ('MESH', 'CURVE', 'FONT'), LineType),
            ("points_export", "Vertices", ('MESH', 'CURVE', 'FONT'), PointType),
            ("curves_export", "Curves", ('CURVE',), CurveType),
            ("texts_export", "Texts", ('FONT',), TextType),
            ("empties_export", "Empties", ('EMPTY',), EmptyType),
            ("cameras_export", "Cameras", ('CAMERA',), CameraType),
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
            settings = entities_settings_dic.get(entity_type.__name__)
            if not settings:
                continue
            link_row = geom_split.row(align=True)
            link_row.prop(settings, "use_default", text="",
                      icon='LINKED' if settings.use_default else 'UNLINKED')
            # NO_EXPORT is the same for all entity enums
            is_export = getattr(self, prop) != NO_EXPORT
            link_row.active = is_export
            if is_export and not settings.use_default:
                split = col.split(factor=0.02)
                split.label(text="")
                box = split.box()                
                if settings:
                    settings.layer_settings.draw(box, obj_name=name)
                    settings.color_settings.draw(box, obj_name=name)
        # TODO Add custom settings for dimensions
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