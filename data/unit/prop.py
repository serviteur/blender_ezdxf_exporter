import bpy


class PreferencesSettings(bpy.types.PropertyGroup):
    unit: bpy.props.EnumProperty(
        items=(
            ("None",) * 3,
            ("Metre",) * 3,
            ("Inch",) * 3,
            ("Foot",) * 3,
            ("Yard",) * 3,
            ("Mile",) * 3,
        ),
        default="Metre",
        name="Unit",
    )
    multiple: bpy.props.EnumProperty(
        items=(
            ("Milli", "Milli", "Divide unit by 1000"),
            ("Centi", "Centi", "Divide unit by 100"),
            ("Deci", "Deci", "Divide unit by 10"),
            ("None", "None", "Use Regular Unit"),
            ("Deca", "Deca", "Multiply unit by 10"),
            ("Hecto", "Hecto", "Multiply unit by 100"),
            ("Kilo", "Kilo", "Multiply unit by 1000"),
        ),
        default="None",
        name="Multiple",
    )
    display_numbers: bpy.props.EnumProperty(
        items=(
            ("1", "Scientific", "Scientific notation (eg 2.35e10^5)"),
            ("2", "Decimal", "Decimal notation"),
            ("3", "Engineering", "Engineering notation"),
            ("4", "Architectural", "Architectural notation"),
            ("5", "Fractional", "Fractional notation"),
        ),
        default="2",
        name="Display numbers",
    )
    display_angles: bpy.props.EnumProperty(
        items=(
            ("0", "Decimal degrees", ""),
            ("1", "Degrees/minutes/seconds", ""),
            ("2", "Grad", ""),
            ("3", "Radians", ""),
        ),
        default="0",
        name="Display angles",
    )

    @property
    def use_imperial(self):
        return self.unit != "Metre"
