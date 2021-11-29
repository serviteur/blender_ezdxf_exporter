def draw(self, layout, context):
    self.filter.draw(layout)
    self.data.draw(layout, self.get_objects(context), self.entities, self.text)
    layer_box = self.default_layer.draw(layout)
    self.layer_global.draw(layer_box)
    self.default_color.draw(layout)
    self.transform.draw(layout)
