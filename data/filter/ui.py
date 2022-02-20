from .constants import ExportObjects


def draw(self, layout):
    layout.label(text="Filter")
    filter_box_box = layout.box()
    col = filter_box_box.column(align=True)
    split = col.split(factor=0.3)
    split.label(text="Export")
    split.prop(self, "export_objects", text="")
    split = col.split(factor=0.3)
    split.label(text="Excluded as")
    split.prop(self, "export_excluded", text="")
    split.active = self.export_objects not in (
        ExportObjects.SELECTED.value,
        ExportObjects.VISIBLE.value,
    )
