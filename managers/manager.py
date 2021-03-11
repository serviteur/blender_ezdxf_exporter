class Manager:
    def __init__(self, exporter) -> None:
        self.exporter = exporter
    
    def create_and_transform_entity(self, entity_func, use_matrix, dxfattribs):
        entity = entity_func()
        dx, dy, dz = self.exporter.settings.transform_settings.delta_xyz if use_matrix else (
            0, 0, 0)
        entity.translate(dx, dy, dz)
        if dxfattribs.get("transparency"):
            entity.transparency = dxfattribs.get("transparency") / 10
        return entity
    
    def select_objects(self, attr, value, _type):
        "If _type objects are not set to render as value, returns them.\nElse returns an empty List"
        exp = self.exporter
        export_as = getattr(exp.settings.data_settings, attr) == value
        type_objects = []
        for i in range(len(exp.objects) - 1, -1, -1):
            if exp.objects[i].type == _type and not export_as:
                type_objects.append(exp.objects.pop(i))
        return type_objects
