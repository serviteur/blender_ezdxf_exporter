from .helper import source_has_alpha
from .constants import EntityColor


def draw(self, layout, obj_name=None):
    if obj_name is None:
        obj_name = "Default Object"
    layout.label(text=obj_name + " Color")
    color_box = layout.box()
    color_box.prop(self, "entity_color_to", text="")
    if self.entity_color_to == EntityColor.ACI.value:
        row = color_box.row()
        row.prop(self, "entity_color_aci")
        color_box.label(text="Find Palette in Preferences", icon="INFO")
    elif self.entity_color_to == EntityColor.CUSTOM.value:
        row = color_box.row()
        row.prop(self, "entity_color_custom")
    col = color_box.column(align=False, heading="Transparency")
    col.use_property_decorate = False
    col.use_property_split = True
    row = col.row(align=True)
    sub = row.row(align=True)
    sub.prop(self, "entity_color_use_transparency", text="")
    sub = sub.row(align=True)
    link = sub.row()
    link.prop(
        self,
        "entity_color_transparency_link",
        text="",
        icon="LINKED" if self.entity_color_transparency_link else "UNLINKED",
    )
    link.active = source_has_alpha(self.entity_color_to)
    val = sub.row()
    val.prop(self, "entity_color_transparency", text="")
    val.active = not self.entity_color_transparency_link or not link.active
    sub.active = self.entity_color_use_transparency
