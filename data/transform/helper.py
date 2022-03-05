from math import pi
from mathutils import Matrix, Euler
from ezdxf_exporter.data.transform.constants import UCS


def get_ucs_matrix(ucs_enum, context):
    if ucs_enum == UCS.GLOBAL.value:
        return Matrix.Identity(4)
    elif ucs_enum == UCS.CAMERA.value:
        active_camera = context.scene.camera
        return active_camera.matrix_world.inverted()
    elif ucs_enum == UCS.FRONT.value:
        return Matrix.Rotation(-pi / 2, 4, "X")
    elif ucs_enum == UCS.BACK.value:
        return Matrix.LocRotScale(None, Euler((-pi / 2, pi, 0)), None)
    elif ucs_enum == UCS.LEFT.value:
        return Matrix.LocRotScale(None, Euler((-pi / 2, -pi / 2, 0)), None)
    elif ucs_enum == UCS.RIGHT.value:
        return Matrix.LocRotScale(None, Euler((-pi / 2, pi / 2, 0)), None)
    elif ucs_enum == UCS.BOTTOM.value:
        return Matrix.Rotation(pi, 4, "X")

    return Matrix.Identity(4)


def update_export_scale(self, context):
    if not self.uniform_export_scale:
        return
    if self.export_scale[0] != self.export_scale[1]:
        self.export_scale[1] = self.export_scale[0]
        return
    if self.export_scale[0] != self.export_scale[2]:
        self.export_scale[2] = self.export_scale[0]
