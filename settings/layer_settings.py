from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
    StringProperty,
)


class EntityLayer(Enum):
    NONE = "Default (Layer 0)"
    COLLECTION = "Collection"
    OBJECT_NAME = "Object Name"
    DATA_NAME = "Data/Mesh Name"
    SCENE_NAME = "Current Scene Name"
    MATERIAL = "Object 1st Material"


class GlobalLayerSettings(PropertyGroup):
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
        mat_layer = layout.split(factor=0.9, align=True)
        mat_layer.prop(self, "material_layer_export")
        mat_layer_link = mat_layer.row()
        mat_layer_link.prop(
            self,
            "material_layer_export_only_selected",
            text="",
            icon="LINKED" if self.material_layer_export_only_selected else "UNLINKED",
        )
        mat_layer_link.active = self.material_layer_export


class LayerSettings(PropertyGroup):
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

    def draw(self, layout, obj_name=None):
        if obj_name is None:
            obj_name = "Default Object"
        layout.label(text=obj_name + " Layer")
        layer_box = layout.box()
        layer_box.prop(self, "entity_layer_to", text="")
        row = layer_box.row()
        row.prop(self, "entity_layer_prefix", text="Prefix")
        row.prop(self, "entity_layer_suffix", text="Suffix")
        layer_color_split = layer_box.split(factor=0.5)
        layer_color_split.prop(self, "entity_layer_color")
        layer_setting = layer_color_split.row()
        layer_setting.prop(self, "entity_layer_transparency")
        layer_setting.active = (self.entity_layer_color != "2" and self.entity_layer_to in (
            EntityLayer.OBJECT_NAME.value,
            EntityLayer.MATERIAL.value,
        )) or self.entity_layer_color == "1"
        if self.entity_layer_color == "1":
            layer_box.prop(self, "entity_layer_color_custom_prop_name")
        layer_box.prop(self, "entity_layer_separate")

        return layer_box
