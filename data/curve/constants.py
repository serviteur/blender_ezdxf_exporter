from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class CurveType(Enum):
    NONE = NO_EXPORT
    # SPLINE = 'Spline'
    MESH = "Mesh"
