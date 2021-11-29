from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class CameraType(Enum):
    NONE = NO_EXPORT
    VIEWPORT = "VIEWPORT (Paperspace)"
    # VPORT = 'VPORT (Modelspace)'
    # VIEW = 'VIEW (Modelspace)'
