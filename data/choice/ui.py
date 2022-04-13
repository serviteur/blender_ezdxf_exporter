import bpy
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
from ezdxf_exporter.data.grease_pencil.constants import GreasePencilType

from ezdxf_exporter.data.layer.ui import draw_local as draw_local_layer


def draw_choice_settings(settings, layout, context):
    self = settings.choice
    layout.label(text="Export Data")
    geometry_box = layout.box()
    col = geometry_box.column(align=True)
    lookup_type_dic = {}
    for obj in settings.get_objects(context):
        lookup_type_dic[obj.type] = True
    entities_settings_dic = {}
    for entity_settings in settings.entities:
        entities_settings_dic[entity_settings.id] = entity_settings
    i = -1
    for prop, name, _types, entity_type in (
        ("faces_export", "Faces", ("MESH", "CURVE", "FONT"), FaceType),
        ("lines_export", "Edges", ("MESH", "CURVE", "FONT", "GPENCIL"), LineType),
        ("points_export", "Vertices", ("MESH", "CURVE", "FONT", "GPENCIL"), PointType),
        ("curves_export", "Curves", ("CURVE",), CurveType),
        ("gpencil_export", "Gr.Pencils", ("GPENCIL",), GreasePencilType),
        ("texts_export", "Texts", ("FONT",), TextType),
        ("empties_export", "Empties", ("EMPTY",), EmptyType),
        ("cameras_export", "Cameras", ("CAMERA",), CameraType),
    ):
        i += 1
        type_supported = False
        for _type in _types:
            if lookup_type_dic.get(_type) is not None:
                type_supported = True
                break
        if not type_supported:
            continue

        geom_split = col.split(factor=0.3, align=True)
        geom_split.label(text=name)
        geom_split = geom_split.split(factor=0.9, align=True)
        geom_split.prop(self, prop, text="")

        entities_settings = entities_settings_dic.get(entity_type.__name__)
        if not entities_settings:
            continue
        link_row = geom_split.row(align=True)
        link_row.prop(entities_settings, "use_default", text="", icon="LINKED" if entities_settings.use_default else "UNLINKED")
        # NO_EXPORT is the same for all entity enums
        is_export = getattr(self, prop) != NO_EXPORT
        link_row.active = is_export

        # Draw text settings if exporting MTEXT
        if prop == "texts_export" and getattr(self, prop) == TextType.MTEXT.value:
            settings.text.draw(col)

        if is_export and not entities_settings.use_default:
            split = col.split(factor=0.02)
            split.label(text="")
            box = split.box()
            if entities_settings:
                draw_local_layer(entities_settings.layer, box, obj_name=name, is_default_layer=False)
                entities_settings.color.draw(box, obj_name=name)

    # TODO Add custom settings for dimensions
    self.use_dimensions = (
        "Annotations" in bpy.data.grease_pencils and "RulerData3D" in bpy.data.grease_pencils["Annotations"].layers
    )
    if self.use_dimensions:
        dim_row = col.split(factor=0.3, align=True)
        dim_row.label(text="Measures")
        dim_row.prop(self, "dimensions_export", text="")

    geometry_box.prop(self, "use_blocks")
