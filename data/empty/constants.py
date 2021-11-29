from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class EmptyType(Enum):
    NONE = NO_EXPORT
    BLOCK = "Block"
    POINT = "POINT"
    # TODO Export Empty as its viewport Geometry ?
