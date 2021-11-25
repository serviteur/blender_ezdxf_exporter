import bpy


class ColorPropertyGroup(bpy.types.PropertyGroup):
    value: bpy.props.FloatVectorProperty(subtype="COLOR", set=lambda s, c: None, get=lambda s: s["value"], min=0, max=1)
