"""
Base module required for Blender registration
"""

import subprocess
import pkg_resources
import sys
from . import auto_load

bl_info = {
    "name": "DXF Exporter",
    "author": "Gorgious",
    "description": """Multifunction DXf exporter""",
    "blender": (2, 93, 0),
    "version": (0, 0, 3),
    "location": "",
    "warning": "",
    "category": "Import-Export",
}


def ensure_ezdxf():
    # Check if module is installed : https://stackoverflow.com/a/44210735/7092409
    # Also https://devtalk.blender.org/t/can-3rd-party-modules-ex-scipy-be-installed-when-an-add-on-is-installed/9709/10
    if "ezdxf" not in {pkg.key for pkg in pkg_resources.working_set}:
        # Install 3rd party modules : https://blender.stackexchange.com/a/153520/86891
        py_exec = sys.executable
        # ensure pip is installed & update
        subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
        subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.call([str(py_exec), "-m", "pip", "install", f"--target={str(py_exec)[:-14]}" + "lib", "ezdxf"])
        if "ezdxf" in {pkg.key for pkg in pkg_resources.working_set}:
            print(" - DXF Exporter : ezdxf installed. Good to go !")


ensure_ezdxf()


def register():
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
