def draw_settings(unit_settings, layout, use_box=False):
    layout.label(text="Units")
    if use_box:
        layout = layout.box()
    layout.prop(unit_settings, "unit")
    layout.prop(unit_settings, "multiple")
    layout.prop(unit_settings, "display_numbers")
    layout.prop(unit_settings, "display_angles")


def draw_preferences(settings, layout):
    draw_settings(settings.unit, layout)
