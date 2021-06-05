from enum import Enum
from .manager import Manager
from ezdxf.math import Vec3


class CameraManager(Manager):
    "Manager for Camera creation and instantation"
    class ViewportFlags(Enum):
        "Enum internally used for viewport settings"
        PERSPECTIVE = 1
        FRONT_CLIP = 2
        BACK_CLIP = 4
        UCS_FOLLOW = 8 # Zooms out every time you enter the viewport. Don't use  !
        FRON_CLIP_NOT_AT_EYE = 16
        UCS_ICON_VISIBILITY = 32
        UCS_ICON_ORIGIN = 64
        FAST_ZOOM = 128
        SNAP_MODE = 256
        GRID_MODE = 512
        ISOMETRIC_SNAP = 1024
        HIDE_PLOT = 2048
        ZOOM_LOCKING = 16384

    def initialize_camera(self, camera_obj, callback):
        "Place camera according to world coordinates in Blender. Automatically converts to Orthographic mode"
        exp = self.exporter
        render = self.exporter.context.scene.render
        dim_x, dim_y = render.resolution_x / 10, render.resolution_y / 10 # TODO Silently clamp values
        doc = exp.doc
        cam_data = camera_obj.data

        # Build the matrix to place camera in 3D world
        matrix_cam = camera_obj.matrix_world
        x_local = Vec3(matrix_cam[0][0], matrix_cam[1][0], matrix_cam[2][0]).normalize()
        y_local = Vec3(matrix_cam[0][1], matrix_cam[1][1], matrix_cam[2][1]).normalize()
        z_local = Vec3(matrix_cam[0][2], matrix_cam[1][2], matrix_cam[2][2]).normalize()

        ucs = doc.ucs.new(camera_obj.name)
        ucs.dxf.origin = camera_obj.location
        ucs.dxf.xaxis = x_local
        ucs.dxf.yaxis = y_local

        # MSP Viewport - Didn't manage to make it work
        # https://ezdxf.readthedocs.io/en/stable/tables/vport_table_entry.html?highlight=vport   
        # vport = doc.viewports.new(camera_obj.name)
        # vport.dxf.target_point = camera_obj.location # Doesnt work. Why ??!

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
            camera_obj.location, 
            view_height=cam_data.ortho_scale,
            )
        pp_viewport.dxf.flags = sum((
            self.ViewportFlags.UCS_ICON_VISIBILITY.value,
            self.ViewportFlags.UCS_ICON_ORIGIN.value,
        ))

        # Rotate the camera
        pp_viewport.dxf.view_direction_vector = z_local        
        pp_viewport.dxf.ucs_handle = ucs

        callback(ucs.dxf)