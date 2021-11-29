from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class DimensionType(Enum):
    NONE = NO_EXPORT
    DIM = "DIMENSION"
