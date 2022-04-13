import bpy


def get_all_cameras(context=None):
    if context is None:
        return [c for c in bpy.data.objects if c.type == "CAMERA"]
    else:
        return [c for c in context.scene.objects if c.type == "CAMERA"]


def get_all_camera_names(context=None):
    return [c.name for c in get_all_cameras(context)]
