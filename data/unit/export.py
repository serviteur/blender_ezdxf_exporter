from ezdxf_exporter.core.export.prop import DataExporter
from ezdxf_exporter.core.preferences.helper import get_preferences

from ezdxf_exporter.data.unit.constants import EZDXF_UNIT_MAPPING

class UnitExporter(DataExporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        units_prefs = get_preferences(self.exporter.context).settings.unit
        try:
            index = EZDXF_UNIT_MAPPING.index(units_prefs.multiple.replace("None", "") + units_prefs.unit)
        except ValueError:
            index = EZDXF_UNIT_MAPPING.index(units_prefs.unit)
            self.exporter.log.append("Unit multiple is not valid. Using unit without multiple")
        self.exporter.doc.header["$INSUNITS"] = index
        self.exporter.doc.header["$MEASUREMENT"] = units_prefs.use_imperial - 1  # 0 : Imperial, 1 : Metric
        self.exporter.doc.header["$LUNITS"] = units_prefs.display_numbers
        self.exporter.doc.header["$AUNITS"] = units_prefs.display_angles