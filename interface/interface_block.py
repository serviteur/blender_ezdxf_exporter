from ezdxf.math import UCS
from .interface import Interface


class InterfaceBlock(Interface):
    "Methods for block creation and instantation"
    def get_data_users(self) -> dict:
        "Returns a dict with data as key and object users a values"
        data_obj_dict = {}
        for obj in self.exporter.objects:
            data = obj.data
            if data in data_obj_dict:
                data_obj_dict[data].append(obj)
            else:
                data_obj_dict[data] = [obj]
        return data_obj_dict

    def instantiate_blocks(self):
        "Instantiate objects that share the same data as Blocks. Returns single-user data objects as a list"
        not_blocks = []
        for data, objs in self.get_data_users().items():
            if not objs:
                continue
            if len(objs) == 1:
                not_blocks.append(objs[0])
            else:
                block = self.initialize_block(objs[0], data.name)
                [self.instantiate_block(block=block, obj=obj) for obj in objs]
        return not_blocks

    def initialize_block(self, obj, block_name):
        block = self.exporter.doc.blocks.new(name=block_name)
        self.exporter.interface_mesh.write_object(
            obj=obj, layout=block, use_matrix=False)

    def instantiate_block(self, block, obj):
        exp = self.exporter
        matrix = obj.matrix_world
        scale = matrix.to_scale()
        depsgraph = exp.context.evaluated_depsgraph_get()
        export_obj = obj.evaluated_get(depsgraph)
        dxfattribs = {
            'layer': exp.interface_layer.get_or_create_layer(obj),
            'color': exp.interface_color.get_ACI_color(),
            'xscale': scale[0],
            'yscale': scale[1],
            'zscale': scale[2],
        }
        export_obj.rotation_mode = 'AXIS_ANGLE'
        raa = export_obj.rotation_axis_angle
        ucs = UCS(origin=matrix.to_translation()).rotate(
            (raa[1], raa[2], raa[3]), raa[0])
        blockref = exp.msp.add_blockref(
            block.name, insert=(0, 0, 0), dxfattribs=dxfattribs)
        blockref.transform(ucs.matrix)
        blockref.translate(
            exp.settings.delta_xyz[0], exp.settings.delta_xyz[1], exp.settings.delta_xyz[2])

        if exp.debug_mode:
            exp.log.append(f"{obj.name} was added as a Block")
