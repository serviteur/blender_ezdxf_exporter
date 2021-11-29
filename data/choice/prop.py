import bpy
from bpy.props import (
    EnumProperty,
    BoolProperty,
)
from ezdxf_exporter.core.constants import NO_EXPORT
from ezdxf_exporter.data.text.constants import TextType
from ezdxf_exporter.data.mesh.constants import (
    FaceType,
    LineType,
    PointType,
)
from ezdxf_exporter.data.empty.constants import EmptyType
from ezdxf_exporter.data.camera.constants import CameraType
from ezdxf_exporter.data.curve.constants import CurveType
from ezdxf_exporter.data.dimension.constants import DimensionType
from .ui import draw


class DataSettings(bpy.types.PropertyGroup):
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
        name="Export Faces", default=FaceType.MESH.value, items=[(f_t.value,) * 3 for f_t in FaceType]
    )

    lines_export: EnumProperty(
        name="Export Lines", default=LineType.NONE.value, items=[(l_t.value,) * 3 for l_t in LineType]
    )

    points_export: EnumProperty(
        name="Export Points", default=PointType.NONE.value, items=[(p_t.value,) * 3 for p_t in PointType]
    )

    curves_export: EnumProperty(
        name="Export Curves", default=CurveType.MESH.value, items=[(c_t.value,) * 3 for c_t in CurveType]
    )

    texts_export: EnumProperty(
        name="Export Texts", default=TextType.MTEXT.value, items=[(t_t.value,) * 3 for t_t in TextType]
    )

    empties_export: EnumProperty(
        name="Export Empties", default=EmptyType.NONE.value, items=[(e_t.value,) * 3 for e_t in EmptyType]
    )

    cameras_export: EnumProperty(
        name="Export Cameras", default=CameraType.VIEWPORT.value, items=[(c_t.value,) * 3 for c_t in CameraType]
    )

    dimensions_export: EnumProperty(
        name="Export Dimensions",
        description="Export Dimensions extracted from the built-in Measure Tool\nWarning : Works only with XY Planar dimensions",
        default=DimensionType.DIM.value,
        items=[(d_t.value,) * 3 for d_t in DimensionType],
    )

    use_dimensions: BoolProperty(
        name="Export Dimensions",
        default=False,
    )

    use_blocks: BoolProperty(
        name="Linked objects as Blocks",
        description="Export objects that share the same mesh data as Block entities, unless the object has an active modifier.",
        default=True,
    )

    def draw(self, layout, objects, entities_properties, text_settings):
        draw(self, layout, objects, entities_properties, text_settings)

    def get_sub_layer_suffix(self, entity_type):
        # TODO : Add customization in addonprefs
        suffix = self.sub_layers_suffixes.get(entity_type, "")
        return suffix if suffix == "" else ("_" + suffix)
