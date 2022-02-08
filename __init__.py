"""
Base module required for Blender registration
"""

import site
import os
from . import auto_load

bl_info = {
    "name": "DXF Exporter",
    "author": "Gorgious",
    "description": """Multifunction DXf exporter""",
    "blender": (2, 93, 0),
    "version": (0, 0, 4),
    "location": "",
    "warning": "",
    "category": "Import-Export",
}

site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))

def register():
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
