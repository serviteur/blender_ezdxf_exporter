def draw_preferences(settings, layout):
    unit_settings = settings.unit
    layout.prop(unit_settings, "unit")
    layout.prop(unit_settings, "multiple")
