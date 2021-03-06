"""
Base module required for Blender registration
"""

from . import auto_load

bl_info = {
    "name": "DXF Exporter",
    "author": "Gorgious",
    "description":
        """Multifunction DXf exporter""",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Import-Export"
}

al = auto_load.AutoLoad()


def register():
    al.register()


def unregister():
    al.unregister()
