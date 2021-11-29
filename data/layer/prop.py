import bpy
from bpy.props import (
    EnumProperty,
    BoolProperty,
    StringProperty,
)
from .ui import draw_global, draw_local
from .constants import EntityLayer


class GlobalLayerSettings(bpy.types.PropertyGroup):
    material_layer_export: BoolProperty(
        name="Export Materials as Layers",
        description="Export Materials as Layers",
        default=False,
    )

    material_layer_export_only_selected: BoolProperty(
        name="Only Exported",
        description="Export Only Materials linked to exported objects\nUncheck to import all materials in current scene",
        default=True,
    )

    def draw(self, layout):
        draw_global(self, layout)


class LayerSettings(bpy.types.PropertyGroup):
    entity_layer_prefix: StringProperty(
        name="Layer Prefix",
        default="",
        description="Prefix layer with this",
    )

    entity_layer_suffix: StringProperty(
        name="Layer Suffix",
        default="",
        description="Suffix layer with this",
    )

    entity_layer_to: EnumProperty(
        name="Object Layer",
        default=EntityLayer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,) * 3 for e_l in EntityLayer],
    )

    entity_layer_separate: BoolProperty(
        name="Export Entities on Sub-Layer",
        description="Different Entity Types (MESH, POINT, MTEXT...) are drawn on separate sub-layers",
        default=False,
    )

    entity_layer_color: EnumProperty(
        name="Color",
        description="Set layer color",
        default="0",
        items=(
            ("0", "Source", "Collection>Tag\nObject>Object Color\nMaterial>Diffuse color\nOther>Default(white)"),
            ("1", "Custom Property", ""),
            ("2", "Default Color (White)", ""),
        ),
    )

    entity_layer_color_custom_prop_name: StringProperty(
        name="Name",
        description="Custom Property which holds the RGB or RGBA or ACI value",
    )

    entity_layer_color_parent: BoolProperty(
        name="Use Parent",
        description="Set layer color to parent collection if color tag isn't set.\nRecursively search for parent collection tag until it finds one.\nDefaults to Black if no color tag is set in hierarchy",
        default=True,
    )

    entity_layer_transparency: BoolProperty(
        name="Transparency",
        description="Set layer transparency if available in source Color",
        default=False,
    )


class PreferencesSettings(bpy.types.PropertyGroup):
    layer_prefix: bpy.props.StringProperty(name="Default Layer Prefix")
    layer_suffix: bpy.props.StringProperty(name="Default Layer Suffix")
    use_prefix_suffix_prefs: BoolProperty(
        name="Use Default Layer Prefix and Suffix",
        description="If enabled, this option will automatically add the preferences Prefix and Suffix in layer names",
        default=False,
    )
