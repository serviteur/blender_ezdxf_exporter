from mathutils import Matrix
from bpy.types import Object
from ezdxf_exporter.core.export.prop import DataExporter
from ezdxf_exporter.data.transform.constants import UCS


class TransformExporter(DataExporter):
    def get_matrix(self, obj: Object, is_block: bool = False) -> Matrix:
        if is_block:
            return Matrix()
        else:
            settings = self.exporter.settings.transform
            if settings.ucs == UCS.GLOBAL.value:
                ucs_matrix = Matrix.Identity(4)
            elif settings.ucs == UCS.CAMERA.value:
                active_camera = self.exporter.context.scene.camera
                ucs_matrix = active_camera.matrix_world.inverted()
            else:
                ucs_matrix = Matrix.Identity(4)
            matrix = ucs_matrix @ obj.matrix_world
            if settings.export_scale != (1, 1, 1):
                mx = Matrix.Scale(settings.export_scale[0], 4, (1, 0, 0))
                my = Matrix.Scale(settings.export_scale[1], 4, (0, 1, 0))
                mz = Matrix.Scale(settings.export_scale[2], 4, (0, 0, 1))
                matrix = mx @ my @ mz @ matrix
            return matrix

    def get_rotation_axis_angle(self, obj: Object):
        proxy_obj = obj.evaluated_get(self.exporter.context.evaluated_depsgraph_get())
        proxy_obj.rotation_mode = "AXIS_ANGLE"
        return proxy_obj.rotation_axis_angle
