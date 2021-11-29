from enum import Enum
import os
from os import listdir
from os.path import isfile, join, splitext
from ezdxf_exporter.core.constants import NO_EXPORT


class TextType(Enum):
    NONE = NO_EXPORT
    MTEXT = "MText"
    TEXT = "Text"
    MESH = "Mesh"


class FillColor(Enum):
    NONE = "No Fill"
    CUSTOM = "Custom Color"
    ACI = "Autocad Color"
    BACKGROUND = "Background Color"


FONTS_TTF = (
    [
        (f, splitext(f)[0].capitalize(), "")
        for f in listdir("C:/Windows/Fonts")
        if isfile(join("C:/Windows/Fonts", f))
        if splitext(f)[1] == ".ttf"
    ]
    if os.name == "nt"
    else []
)  # TODO : support override fonts for Linux and OSx
