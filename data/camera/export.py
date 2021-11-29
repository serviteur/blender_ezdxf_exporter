from enum import Enum
from mathutils import Vector
from ezdxf_exporter.core.export.prop import DataExporter
from ezdxf.math import Vec3


class CameraExporter(DataExporter):
    "Manager for Camera creation and instantation"
    class ViewportFlags(Enum):
        "Enum internally used for viewport settings"
        PERSPECTIVE = 1
        FRONT_CLIP = 2
        BACK_CLIP = 4
        UCS_FOLLOW = 8  # Zooms out every time you enter the viewport. Don't use  !
        FRON_CLIP_NOT_AT_EYE = 16
        UCS_ICON_VISIBILITY = 32
        UCS_ICON_ORIGIN = 64
        FAST_ZOOM = 128
        SNAP_MODE = 256
        GRID_MODE = 512
        ISOMETRIC_SNAP = 1024
        HIDE_PLOT = 2048
        ZOOM_LOCKING = 16384

    def initialize_camera(self, camera_obj, delta_xyz):
        "Place camera according to world coordinates in Blender. Automatically converts to Orthographic mode"
        exp = self.exporter
        render = self.exporter.context.scene.render
        dim_x, dim_y = render.resolution_x / \
            10, render.resolution_y / 10  # TODO Silently clamp values
        doc = exp.doc
        cam_data = camera_obj.data

        # Retrieve axes and position to place and rotate camera in 3D world
        (translation, rotation, _) = camera_obj.matrix_world.decompose()
        translation += Vector(delta_xyz)
        local_axes = [
            rotation @ vec for vec in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))]

        # Need to explicitly create an ucs to access it in ppspace vport
        ucs = doc.ucs.new(camera_obj.name)
        ucs.dxf.origin = translation
        ucs.dxf.xaxis = local_axes[0]
        ucs.dxf.yaxis = local_axes[1]

        # MSP Viewport - Didn't manage to make it work
        # https://ezdxf.readthedocs.io/en/stable/tables/vport_table_entry.html?highlight=vport
        # vport = doc.viewports.new(camera_obj.name)
        # vport.dxf.center = translation # Doesnt work. Why ??!
        # vport.direction_point = local_axes[2] # Doesnt work. Why ??!

        # View - Didn't manage to make it work
        # https://ezdxf.readthedocs.io/en/stable/tables/view_table_entry.html?highlight=view
        # view = doc.views.new(camera_obj.name)

        # Add camera as a Paperspace Layout
        pp_layout = doc.new_layout(camera_obj.name)
        pp_layout.page_setup()

        # Add a viewport inside the Layout
        pp_viewport = pp_layout.add_viewport(
            (dim_x / 2, dim_y / 2),
            (dim_x, dim_y),
            [translation.dot(axis)
             for axis in local_axes],  # Local camera position
            view_height=cam_data.ortho_scale,
        )
        pp_viewport.dxf.flags = sum((
            self.ViewportFlags.UCS_ICON_VISIBILITY.value,
            self.ViewportFlags.UCS_ICON_ORIGIN.value,
        ))

        # Rotate the camera
        pp_viewport.dxf.ucs_handle = ucs
        pp_viewport.dxf.view_direction_vector = local_axes[2]
