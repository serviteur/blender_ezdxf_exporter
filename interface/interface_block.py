from ezdxf.math import UCS
from .interface import Interface


class InterfaceBlock(Interface):
    def instantiate_blocks(self):
        not_blocks = []
        exp = self.exporter
        data_obj_dict = {}
        for obj in exp.objects:
            data = obj.data
            if data in data_obj_dict:
                data_obj_dict[data].append(obj)
            else:
                data_obj_dict[data] = [obj]
        for data, objs in data_obj_dict.items():
            if not objs:
                continue
            if len(objs) == 1:
                not_blocks.append(objs[0])
            else:
                block = exp.doc.blocks.new(name=data.name)
                exp.interface_mesh.write_object(
                    obj=objs[0], layout=block, use_matrix=False)
                [self.instantiate_block(block=block, obj=obj) for obj in objs]
        return not_blocks

    def instantiate_block(self, block, obj):
        exp = self.exporter
        matrix = obj.matrix_world
        scale = matrix.to_scale()
        depsgraph = exp.context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)
        dxfattribs = {
            'layer': exp.interface_layer.create_layer_if_needed_and_get_name(obj),
            'color': exp.interface_color.get_ACI_color(),
            'xscale': scale[0],
            'yscale': scale[1],
            'zscale': scale[2],
        }
        export_obj.rotation_mode = 'AXIS_ANGLE'
        raa = export_obj.rotation_axis_angle
        ucs = UCS(origin=matrix.to_translation()).rotate(
            (raa[1], raa[2], raa[3]), raa[0])
        blockref = exp.msp.add_blockref(block.name, insert=(0, 0, 0), dxfattribs=dxfattribs)
        blockref.transform(ucs.matrix)
        blockref.translate(
            exp.settings.delta_xyz[0], exp.settings.delta_xyz[1], exp.settings.delta_xyz[2])

        if exp.debug_mode:
            exp.log.append(f"{obj.name} was added as a Block")
