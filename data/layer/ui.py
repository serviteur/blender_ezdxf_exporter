from .constants import EntityLayer


def draw_global(self, layout):
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


def draw_local(self, layout, context, obj_name=None):
    prefs = context.preferences.addons["ezdxf_exporter"].preferences.layer_preferences
    if obj_name is None:
        obj_name = "Default Object"
    layout.label(text=obj_name + " Layer")
    layer_box = layout.box()
    layer_box.prop(self, "entity_layer_to", text="")
    row = layer_box.row()
    use_prefs_prefix_suffix = self.entity_layer_preferences_prefix_suffix
    if use_prefs_prefix_suffix:
        sub_row = row.row()
        sub_row.prop(prefs, "layer_prefix", text="Prefix")
        sub_row.prop(prefs, "layer_suffix", text="Suffix")
        sub_row.enabled=False
    else:
        row.prop(self, "entity_layer_prefix", text="Prefix")
        row.prop(self, "entity_layer_suffix", text="Suffix")
    row.prop(self, "entity_layer_preferences_prefix_suffix", icon="LINKED" if use_prefs_prefix_suffix else "UNLINKED", text="",)
    layer_color_split = layer_box.split(factor=0.5)
    layer_color_split.prop(self, "entity_layer_color")
    layer_setting = layer_color_split.row()
    layer_setting.prop(self, "entity_layer_transparency")
    layer_setting.active = (
        self.entity_layer_color != "2"
        and self.entity_layer_to
        in (
            EntityLayer.OBJECT_NAME.value,
            EntityLayer.MATERIAL.value,
        )
    ) or self.entity_layer_color == "1"
    if self.entity_layer_color == "1":
        layer_box.prop(self, "entity_layer_color_custom_prop_name")
    layer_box.prop(self, "entity_layer_separate")

    return layer_box


def draw_preferences(settings, layout):
    layout.prop(settings, "layer_prefix")
    layout.prop(settings, "layer_suffix")
    layout.prop(settings, "use_prefix_suffix_prefs")
