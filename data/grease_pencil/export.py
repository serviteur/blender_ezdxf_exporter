from ezdxf_exporter.core.export.prop import DataExporter


class GreasePencilExporter(DataExporter):
    def write_gpencil_object(self, layout, gpencil_object, dxfattribs, callback, matrix):
        "Export gp object as Edges"

        gp = gpencil_object.data
        z_scale_export = self.exporter.settings.transform.export_scale[2]
        polyline_func = layout.add_lwpolyline if z_scale_export == 0 else layout.add_polyline3d
        for layer in gp.layers:
            for stroke in layer.frames[0].strokes:
                print(stroke)
                polyline = polyline_func([matrix @ point.co for point in stroke.points], dxfattribs=dxfattribs)
                callback(polyline)
                
