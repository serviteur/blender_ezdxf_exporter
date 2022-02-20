from enum import Enum
from ezdxf_exporter.core.constants import NO_EXPORT


class ExcludedObject(Enum):
    NONE = NO_EXPORT
    THAWED = "Thawed"
    FROZEN = "Frozen"


class ExportObjects(Enum):
    SELECTED = "Only Selected"
    VISIBLE = "Only Visible"
    SCENE = "Current Scene"
    # VIEW_LAYER = "Current View Layer"
    ALL = "All Objects in file"
