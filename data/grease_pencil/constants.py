from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class GreasePencilType(Enum):
    NONE = NO_EXPORT
    MESH = "MESH"
    # CURVES = "CURVES"
