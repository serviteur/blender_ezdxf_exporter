from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolVectorProperty,
    BoolProperty
)


class EntityLayer(Enum):
    NONE = 'Default (Layer 0)'
    COLLECTION = 'Collection'
    OBJECT_NAME = 'Object Name'
    DATA_NAME = 'Data/Mesh Name'
    SCENE_NAME = 'Current Scene Name'
    MATERIAL = 'Object 1st Material'


class ExcludedObject(Enum):
    NONE = "No Export"
    THAWED = "Thawed"
    FROZEN = "Frozen"


class LayerSettings(PropertyGroup):
    entity_layer_to: EnumProperty(
        name="Object Layer",
        default=EntityLayer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,)*3 for e_l in EntityLayer])

    entity_layer_separate: BoolProperty(
        name="Export Entities on Sub-Layers",
        description="Different Entity Types (MESH, POINT, MTEXT...) are drawn on separate sub-layers",
        default=True,
    )

    entity_layer_color: BoolProperty(
        name="Color",
        description="Set layer color if available in source",
        default=True,
    )

    entity_layer_links: BoolVectorProperty(
        name="Link Layer",
        description="Link layer to source color.\nIf set to false, layer will take default values",
        size=3,
        default=(True, True, True),
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

    material_layer_export: BoolProperty(        
        name="Materials as Layers",
        description="Export Materials as Layers",
        default=False,
    )
    
    material_layer_export_only_selected: BoolProperty(        
        name="Only Exported",
        description="Export Only Materials linked to exported objects\nUncheck to import all materials in current scene",
        default=True,
    )

    layer_excluded_export: EnumProperty(
        name="Export Excluded as",
        description="If collections are excluded from current view_layer, choose how to export them",
        default=ExcludedObject.FROZEN.value,
        items=[(e_c_t.value,) * 3 for e_c_t in ExcludedObject],
    )

    def draw(self, layout, only_selected):
        layout.label(text="Object Layer")
        layer_box = layout.box()
        layer_box.prop(self, "entity_layer_to", text="")
        if not only_selected and self.entity_layer_to in (
                EntityLayer.COLLECTION.value,
                EntityLayer.OBJECT_NAME.value,
        ):
            split = layer_box.split(factor=0.5)
            split.label(text="Export Excluded as")
            split.prop(self, "layer_excluded_export", text="")
        layer_color_split = layer_box.split(factor=0.5)
        layer_color_split.prop(self, "entity_layer_color")
        layer_setting = layer_color_split.row()
        layer_setting.prop(self, "entity_layer_transparency")
        layer_setting.active = self.entity_layer_color and self.entity_layer_to in (
            EntityLayer.OBJECT_NAME.value, EntityLayer.MATERIAL.value)
        layer_box.prop(self, "entity_layer_separate")
        mat_layer = layer_box.split(factor=0.9, align=True)
        mat_layer.prop(self, "material_layer_export")
        mat_layer_link = mat_layer.row()
        mat_layer_link.prop(self, "material_layer_export_only_selected", text="", icon='LINKED' if self.material_layer_export_only_selected else 'UNLINKED')
        mat_layer_link.active = self.material_layer_export
