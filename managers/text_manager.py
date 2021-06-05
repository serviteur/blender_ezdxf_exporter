from ezdxf.math import UCS
from ..settings.data_settings import TextType
from ..settings.text_settings import FillColor
from .manager import Manager
import ntpath


class TextManager(Manager):
    MTEXT_ATTACHMENT_POINTS_DIC = {
        'MTEXT_TOP_LEFT': 1,
        'MTEXT_TOP_CENTER': 2,
        'MTEXT_TOP_RIGHT': 3,
        'MTEXT_MIDDLE_LEFT': 4,
        'MTEXT_MIDDLE_CENTER': 5,
        'MTEXT_MIDDLE_RIGHT': 6,
        'MTEXT_BOTTOM_LEFT': 7,
        'MTEXT_BOTTOM_CENTER': 8,
        'MTEXT_BOTTOM_RIGHT': 9,
    }

    def write_text(self, layout, text_obj, matrix, dxfattribs, callback):
        text = text_obj.data
        align_x, align_y = text.align_x, text.align_y

        scale = matrix.to_scale()

        # Is there no way to directly get an axis angle from matrix ??
        raa = matrix.to_euler().to_quaternion().to_axis_angle()

        if self.exporter.settings.data_settings.texts_export == TextType.MTEXT.value:
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

            # Need to recreate a matrix for 3D location and rotation
            # TODO : put this in math utils :
            ucs = UCS(origin=matrix.to_translation()).rotate(
                (raa[0][0], raa[0][1], raa[0][2]), raa[1])

            text_settings = self.exporter.settings.text_settings
            text_dxf = layout.add_mtext(text.body, dxfattribs)
            text_dxf.dxf.char_height = text.size / \
                2 * (sum(scale) / len(scale))

            # Set Font. If necessary, create a new style per font
            text_font_path = text.font.filepath
            if text_settings.font_override or text_font_path == "<builtin>":  # Override or default blender font
                dxf_font_name = text_settings.font_name
            else:
                dxf_font_name = ntpath.basename(text_font_path)

            if dxf_font_name not in self.exporter.doc.styles:
                self.exporter.doc.styles.new(dxf_font_name, dxfattribs={
                                             "font": dxf_font_name})

            text_dxf.dxf.style = dxf_font_name
            text_dxf.set_location((0, 0, 0), attachment_point=align_dxf)

            # Set Fill
            if text_settings.fill_type != FillColor.NONE.value:
                text_dxf.set_bg_color(
                    text_settings.get_color_value(), scale=text_settings.fill_scale)

        else:
            # Couldn't make custom fonts work with Text object. Use Mtext instead.
            align_dxf = ""
            if align_y in ('TOP', 'BOTTOM'):
                align_dxf = align_y + "_"
            elif align_y == 'CENTER':
                align_dxf = "MIDDLE_"
            if align_x in ('LEFT', 'CENTER', 'RIGHT'):
                align_dxf += align_x
            else:
                align_dxf += "CENTER"
            dxfattribs['height'] = text.size / 2 * (sum(scale) / len(scale))

            # Need to recreate a matrix for 3D location and rotation
            ucs = UCS(origin=matrix.to_translation()).rotate(
                (raa[0][0], raa[0][1], raa[0][2]), raa[1])
            text_dxf = layout.add_text(text.body, dxfattribs)
            text_dxf.set_pos((0, 0, 0), align=align_dxf)
        text_dxf.transform(ucs.matrix)

        callback(text_dxf)
