from mathutils import Vector
from .manager import Manager


class SplineManager(Manager):
    def write_curve(self, layout, curve_obj, matrix, raa, dxfattribs, callback):
        curve = curve_obj.data
        def func_spline(spl):
            if len(spl.points) > 0:
                return layout.add_spline([(matrix @ p.co)[0:3] for p in spl.points])
            else:
                return layout.add_spline([matrix @ p.co for p in spl.bezier_points])

        for spline in curve.splines:
            self.create_and_transform_entity(lambda: func_spline(spline), True, dxfattribs, callback)
