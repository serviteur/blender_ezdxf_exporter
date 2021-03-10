from bpy.types import PropertyGroup
from bpy.props import (
    EnumProperty,
    BoolProperty,
    IntProperty
)
from ..shared_properties import (
    entity_color,
    ACI_Colors,
    
    source_has_alpha,
)


class ColorSettings(PropertyGroup):
    entity_color_to: EnumProperty(
        name="Object Color",
        default=entity_color.BYLAYER.value,
        description="Entity COLOR assigned to ?",
        items=[(e_c.value,)*3 for e_c in entity_color])

    entity_color_use_transparency: BoolProperty(
        name="Use Transparency",
        description="Enable to set color transparency if available in source Color",
        default=False,
    )

    entity_color_transparency_link: BoolProperty(
        name="Link Transparency to source",
        description="Use Alpha value in source color if available",
        default=True,
    )

    entity_color_transparency: IntProperty(
        name="Override Transparency",
        description="Override Transparency on Object",
        default=0,
        min=0,
        max=100,
    )

    entity_color_aci: EnumProperty(
        name="ACI",
        description="Autocad Color Index - Color as an integer [0:255]",
        default=ACI_Colors.WHITE.value[0],
        items=[aci.value for aci in ACI_Colors],
    )
    def draw(self, layout):        
        layout.label(text="Object Color")
        color_box = layout.box()
        color_box.prop(self, "entity_color_to", text="")
        if self.entity_color_to == entity_color.ACI.value:
            aci_color_row = color_box.row()
            aci_color_row.prop(self, "entity_color_aci")        
        col = color_box.column(align=False, heading="Transparency")
        col.use_property_decorate = False
        col.use_property_split = True
        row = col.row(align=True)
        sub = row.row(align=True)
        sub.prop(self, "entity_color_use_transparency", text="")
        sub = sub.row(align=True)
        link = sub.row()
        link.prop(self, "entity_color_transparency_link", text="",icon="LINKED" if self.entity_color_transparency_link else 'UNLINKED')
        link.active = source_has_alpha(self.entity_color_to)
        val = sub.row()
        val.prop(self, "entity_color_transparency", text="")
        val.active = not self.entity_color_transparency_link or not link.active
        sub.active = self.entity_color_use_transparency

