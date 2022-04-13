from enum import Enum


class EntityLayer(Enum):
    NONE = "Default (Layer 0)"
    COLLECTION = "Collection"
    OBJECT_NAME = "Object Name"
    DATA_NAME = "Data/Mesh Name"
    SCENE_NAME = "Current Scene Name"
    MATERIAL = "Object 1st Material"
    CUSTOM_PROP = "Custom Property"
