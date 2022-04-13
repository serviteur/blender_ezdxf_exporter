from enum import Enum

class UCS(Enum):
    GLOBAL = "GLOBAL"
    CAMERA = "CAMERA"
    FRONT = "FRONT"
    BACK = "BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"

UCS_DESCRIPTIONS = {
    UCS.GLOBAL.value: "Global Coordinate System (Default)",
    UCS.CAMERA.value: "Set the camera transform as UCS"
}