from enum import Enum
from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolVectorProperty,
    BoolProperty
)


class entity_layer(Enum):
    NONE = 'Default (Layer 0)'
    COLLECTION = 'Collection'
    OBJECT_NAME = 'Object Name'
    DATA_NAME = 'Mesh Name'
    SCENE_NAME = 'Current Scene Name'
    MATERIAL = 'Current Material'


class LayerSettings(PropertyGroup):
    entity_layer_to: EnumProperty(
        name="Object Layer",
        default=entity_layer.COLLECTION.value,
        description="Entity LAYER assigned to ?",
        items=[(e_l.value,)*3 for e_l in entity_layer])

    entity_layer_separate: BoolVectorProperty(
        name="Face, Edge and Vertex Sub-Layers",
        description="Faces, Lines and Points are drawn on separate sub-layers",
        # TODO : Add customization in addonprefs
        default=(False, False, False)
    )

    entity_layer_color: BoolProperty(
        name="Use Color",
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
        name="Use Transparency",
        description="Set layer transparency if available in source Color",
        default=False,
    )

    def draw(self, layout):
        layout.label(text="Object Layer")
        layer_box = layout.box()
        layer_box.prop(self, "entity_layer_to", text="")
        layer_color_split = layer_box.split(factor=0.5)
        layer_color_split.prop(self, "entity_layer_color", toggle=True)
        layer_setting = layer_color_split.row()
        if self.entity_layer_to == entity_layer.COLLECTION.value:
            layer_setting.prop(self, "entity_layer_color_parent", toggle=True)
            layer_setting.enabled = self.entity_layer_color
        else:
            layer_setting.prop(self, "entity_layer_transparency", toggle=True)
            layer_setting.enabled = self.entity_layer_color and self.entity_layer_to in (
                entity_layer.OBJECT_NAME.value, entity_layer.MATERIAL.value)
        layer_separate = layer_box.column(heading="Sub Layers", align=True)
        layer_separate.use_property_split = True
        layer_separate.use_property_decorate = False
        for i, text in enumerate(("Faces", "Lines", "Points")):
            split = layer_separate.split(factor=0.9, align=True)
            split.prop(self, "entity_layer_separate",
                       index=i, toggle=True, text=text)
            split.prop(self, "entity_layer_links", index=i, text="",
                       icon='LINKED' if self.entity_layer_links[i] else 'UNLINKED')
