import bpy


def set_prop(self, value):
    if self.readonly:
        return
    self["value"] = value
    self.readonly = True


def get_prop(self):
    return self["value"]


class ColorPropertyGroup(bpy.types.PropertyGroup):
    value: bpy.props.FloatVectorProperty(subtype="COLOR", set=set_prop, get=get_prop, min=0, max=1)
    readonly: bpy.props.BoolProperty()
