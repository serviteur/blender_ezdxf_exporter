
def update_export_scale(self, context):
    if not self.uniform_export_scale:
        return
    if self.export_scale[0] != self.export_scale[1]:
        self.export_scale[1] = self.export_scale[0]
        return
    if self.export_scale[0] != self.export_scale[2]:
        self.export_scale[2] = self.export_scale[0]
