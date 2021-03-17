from .manager import Manager


class SplineManager(Manager):
    def write_curve(self, layout, curve_obj, matrix, raa, dxfattribs, callback):
        "Export curve object as Spline"
        # This is mostly not working
        curve = curve_obj.data
        for spline in curve.splines:
            if len(spline.points) > 0:
                spline = layout.add_spline([(matrix @ p.co)[0:3] for p in spline.points])
            else:
                spline = layout.add_spline([matrix @ p.co for p in spline.bezier_points])
            callback(spline)
