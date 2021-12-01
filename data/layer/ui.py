from ezdxf_exporter.core.preferences.helper import get_preferences

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


def draw_local(layer_settings, layout, context, obj_name=None):
    prefs = get_preferences(context).settings.layer
    if obj_name is None:
        obj_name = "Default Object"
    layout.label(text=obj_name + " Layer")
    layer_box = layout.box()
    layer_box.prop(layer_settings, "entity_layer_to", text="")
    row = layer_box.row()
    use_prefs_prefix_suffix = layer_settings.entity_layer_preferences_prefix_suffix
    if use_prefs_prefix_suffix:
        sub_row = row.row()
        sub_row.prop(prefs, "layer_prefix", text="Prefix")
        sub_row.prop(prefs, "layer_suffix", text="Suffix")
        sub_row.enabled = False
    else:
        row.prop(layer_settings, "entity_layer_prefix", text="Prefix")
        row.prop(layer_settings, "entity_layer_suffix", text="Suffix")
    row.prop(
        layer_settings,
        "entity_layer_preferences_prefix_suffix",
        icon="LINKED" if use_prefs_prefix_suffix else "UNLINKED",
        text="",
    )
    layer_color_split = layer_box.split(factor=0.5)
    layer_color_split.prop(layer_settings, "entity_layer_color")
    layer_setting = layer_color_split.row()
    layer_setting.prop(layer_settings, "entity_layer_transparency")
    layer_setting.active = (
        layer_settings.entity_layer_color != "2"
        and layer_settings.entity_layer_to
        in (
            EntityLayer.OBJECT_NAME.value,
            EntityLayer.MATERIAL.value,
        )
    ) or layer_settings.entity_layer_color == "1"
    if layer_settings.entity_layer_color == "1":
        layer_box.prop(layer_settings, "entity_layer_color_custom_prop_name")
    layer_box.prop(layer_settings, "entity_layer_separate")

    return layer_box


def draw_preferences(settings, layout):
    layer_settings = settings.layer
    layout.prop(layer_settings, "layer_prefix")
    layout.prop(layer_settings, "layer_suffix")
    layout.prop(layer_settings, "use_prefix_suffix_prefs")
    layout.label(text="Sub-layer suffixes :")
    for attr in layer_settings.sub_layers_suffixes_attrs.values():
        layout.prop(layer_settings, attr)
