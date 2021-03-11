from ezdxf.math import UCS
from .manager import Manager
from ..settings.data_settings import empty_type


class BlockManager(Manager):
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

    def initialize_block(self, name):
        return self.exporter.doc.blocks.new(name=name)

    def initialize_blocks(self):
        """Initialize objects that share the same data as Blocks. 
    Returns :
    Arg 1 : Dictionary with one of the objects as a key, and a tuple (n=2) containing the block (i=0) and a list will all linked objects (i=1) as a value
    Arg 2 : List containing single-user data objects"""
        blocks_dic = {}
        not_blocks = []
        for data, objs in self.get_data_users().items():
            if not objs:
                continue
            if len(objs) == 1:
                not_blocks.append(objs[0])
            else:
                blocks_dic[objs[0]] = (self.initialize_block(data.name), objs)
        return blocks_dic, not_blocks

    def instantiate_block(self, block, obj, matrix, raa, dxfattribs):
        exp = self.exporter
        scale = matrix.to_scale()
        dxfattribs.update({
            'xscale': scale[0],
            'yscale': scale[1],
            'zscale': scale[2],
        })
        ucs = UCS(origin=matrix.to_translation()).rotate(
            (raa[1], raa[2], raa[3]), raa[0])
        blockref = exp.msp.add_blockref(
            block.name, insert=(0, 0, 0), dxfattribs=dxfattribs)
        blockref.transform(ucs.matrix)
        dx, dy, dz = exp.settings.transform_settings.delta_xyz
        blockref.translate(dx, dy, dz)

        if exp.debug_mode:
            exp.log.append(f"{obj.name} was added as a Block")
