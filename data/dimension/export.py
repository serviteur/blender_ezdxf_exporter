from ezdxf.math import UCS
from ezdxf_exporter.core.export.prop import DataExporter


class DimensionExporter(DataExporter):
    "Methods to initialize and instantiate dimensions"
    def add_aligned_dim(self, p1, p2, distance=1, precision=2):
        # TODO : Place dimensions in 3D world with UCS
        line = self.exporter.msp.add_aligned_dim(p1=p1, p2=p2, distance=distance, dxfattribs={
                                   'layer': "Dimensions"})
        line.set_text_format(dec=precision)
        line.render(UCS(origin=(0, 0, (p1[2] + p2[2]) / 2)))

