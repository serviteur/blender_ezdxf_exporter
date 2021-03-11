class Manager:
    def __init__(self, exporter) -> None:
        self.exporter = exporter
    
    def create_and_transform_entity(self, entity_func, use_matrix, dxfattribs):
        entity = entity_func()
        if entity is not None:
            dx, dy, dz = self.exporter.settings.transform_settings.delta_xyz if use_matrix else (
                0, 0, 0)
            entity.translate(dx, dy, dz)
            if dxfattribs.get("transparency"):
                entity.transparency = dxfattribs.get("transparency") / 10
        return entity
