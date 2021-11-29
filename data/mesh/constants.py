from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class FaceType(Enum):
    NONE = NO_EXPORT
    MESH = "MESH"
    FACES3D = "3DFACEs"
    POLYFACE = "POLYFACE"


class LineType(Enum):
    NONE = NO_EXPORT
    LINES = "LINEs"
    POLYLINES = "POLYLINEs"


class PointType(Enum):
    NONE = NO_EXPORT
    POINTS = "POINTs"
