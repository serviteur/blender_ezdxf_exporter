from ezdxf.math import UCS
from ..settings.data_settings import text_type
from .manager import Manager


class TextManager(Manager):
    MTEXT_ATTACHMENT_POINTS_DIC = {
        'MTEXT_TOP_LEFT' : 1,
        'MTEXT_TOP_CENTER' : 2,
        'MTEXT_TOP_RIGHT' : 3,
        'MTEXT_MIDDLE_LEFT' : 4,
        'MTEXT_MIDDLE_CENTER' : 5,
        'MTEXT_MIDDLE_RIGHT' : 6,
        'MTEXT_BOTTOM_LEFT' : 7,
        'MTEXT_BOTTOM_CENTER' : 8,
        'MTEXT_BOTTOM_RIGHT' : 9,
    }

    def select_text_objects(self):
        "If Text objects are not set to render as Mesh, returns them.\nElse returns an empty List"
        exp = self.exporter
        export_as_mesh = exp.settings.data_settings.texts_export == text_type.MESH.value
        text_objects = []
        for i in range(len(exp.objects) - 1, -1, -1):
            if exp.objects[i].type == 'FONT' and not export_as_mesh:
                text_objects.append(exp.objects.pop(i))
        return text_objects

    def write_text(self, layout, text_obj, matrix, raa, dxfattribs):
        text = text_obj.data
        align_x, align_y = text.align_x, text.align_y

        scale = matrix.to_scale()
        # TODO : Use correct font : Need to know supported ones else file is corrupted

        def entity_func_text():
            align_dxf = ""
            if align_y in ('TOP', 'BOTTOM'):
                align_dxf = align_y + "_"
            elif align_y == 'CENTER':
                align_dxf = "MIDDLE_"
            if align_x in ('LEFT', 'CENTER', 'RIGHT'):
                align_dxf += align_x
            else:
                align_dxf += "CENTER"
            dxfattribs ['height'] = text.size / 2 * (sum(scale) / len(scale))
            ucs = UCS(origin=matrix.to_translation()).rotate(
                (raa[1], raa[2], raa[3]), raa[0])
            text_dxf = layout.add_text(text.body, dxfattribs)
            text_dxf.set_pos((0, 0, 0), align=align_dxf)
            text_dxf.transform(ucs.matrix)
            return text_dxf

        def entity_func_mtext():
            align_dxf = "MTEXT_"
            if align_y in ('TOP', 'BOTTOM'):
                align_dxf += align_y + "_"
            elif align_y == 'CENTER':
                align_dxf += "MIDDLE_"
            elif align_y.startswith("TOP"):
                align_dxf += "TOP_"
            elif align_y.startswith("BOTTOM"):
                align_dxf += "BOTTOM_"
            if align_x in ('LEFT', 'CENTER', 'RIGHT'):
                align_dxf += align_x
            else:
                align_dxf += "CENTER"
            align_dxf = self.MTEXT_ATTACHMENT_POINTS_DIC.get(align_dxf, 1)

            ucs = UCS(origin=matrix.to_translation()).rotate(
                (raa[1], raa[2], raa[3]), raa[0])
            text_dxf = layout.add_mtext(text.body, dxfattribs)
            text_dxf.dxf.char_height = text.size / 2 * (sum(scale) / len(scale))
            text_dxf.set_location((0, 0, 0), attachment_point=align_dxf)
            text_dxf.transform(ucs.matrix)
            return text_dxf

        self.create_and_transform_entity(
            entity_func_mtext if self.exporter.settings.data_settings.texts_export == text_type.MTEXT.value else entity_func_text,
            True,
            dxfattribs)
