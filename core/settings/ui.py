from ezdxf_exporter.data.choice.ui import draw_choice_settings
from ezdxf_exporter.data.layer.ui import draw_local as draw_local_layer
from ezdxf_exporter.data.unit.ui import draw_settings as draw_units

def draw(self, layout, context):
    self.filter.draw(layout)
    draw_choice_settings(self, layout, context)
    layer_box = draw_local_layer(self.default_layer, layout, context)
    self.layer_global.draw(layer_box)
    self.default_color.draw(layout)
    draw_units(self.unit, layout, use_box=True)
    self.transform.draw(layout)
