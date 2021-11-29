from .constants import ExportObjects


def draw(self, layout):
    layout.label(text="Miscellaneous")
    misc_box = layout.box()
    col = misc_box.column(align=True)
    split = col.split(factor=0.3)
    split.label(text="Export")
    split.prop(self, "export_objects", text="")
    split = col.split(factor=0.3)
    split.label(text="Excluded as")
    split.prop(self, "export_excluded", text="")
    split.active = self.export_objects != ExportObjects.SELECTED.value
