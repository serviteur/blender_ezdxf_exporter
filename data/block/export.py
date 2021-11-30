"""
Takes care of regular BLOCKs logic
"""

from collections import defaultdict

from ezdxf.math import UCS
from ezdxf_exporter.core.export.prop import DataExporter


class BlockExporter(DataExporter):
    "Manager for block creation and instantation"

    def get_data_users(self) -> dict:
        "Returns a dict with data as key and object users as values"
        data_obj_dict = defaultdict(list)
        for obj in self.exporter.objects:
            data_obj_dict[obj.data].append(obj)
        return data_obj_dict

    def initialize_block(self, name):
        "Creates and return a new blank BLOCK entity"
        return self.exporter.doc.blocks.new(name=name)

    def initialize_blocks(self):
        """Initialize objects that share the same data as Blocks.
        Returns :
        Arg 1 : Dictionary with one of the objects as a key, and a tuple (n=2) containing the block (i=0) and a list will all linked objects (i=1) as a value
        Arg 2 : List containing single-user data objects (not to be instantiated as blocks)"""
        blocks_dict = {}
        not_blocks = []
        for data, objs in self.get_data_users().items():
            if not objs:
                continue
            obj = objs[0]
            for i in range(len(objs)):
                # Do not export linked objects as blocks if they have a modifier because 
                # The evaluated mesh may or may not be different for every linked object
                if obj.modifiers:
                    not_blocks.append(objs.pop(0))
            if len(objs) == 1:
                not_blocks.append(obj)
            elif data is None:
                # Linked Empties. TODO : create blocks with linked empties. 
                # For now they are instantiated as regular objects
                # not_blocks.extend(objs)
                blocks_dict[obj] = (self.initialize_block("__Empty__"), objs)
            else:
                blocks_dict[obj] = (self.initialize_block(data.name), objs)
        return blocks_dict, not_blocks

    def instantiate_block(self, block, matrix, raa, dxfattribs, callback=None):
        exp = self.exporter
        scale = matrix.to_scale()
        dxfattribs.update(
            {
                "xscale": scale[0],
                "yscale": scale[1],
                "zscale": scale[2],
            }
        )

        # Add a new block instance at origin
        blockref = exp.msp.add_blockref(block.name, insert=(0, 0, 0), dxfattribs=dxfattribs)
        # Place the block in 3D and rotate it accordingly
        ucs = UCS(origin=matrix.to_translation()).rotate((raa[1], raa[2], raa[3]), raa[0])
        blockref.transform(ucs.matrix)

        if callback:
            callback(blockref)
