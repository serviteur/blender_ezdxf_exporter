import math
import struct


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy, _ = origin
    px, py, _ = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy, 0


def float_to_hex(f):
    return hex(struct.unpack("<I", struct.pack("<f", f))[0])


def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)


def parent_lookup(coll):
    parent_lookup = {}
    for coll in traverse_tree(coll):
        for c in coll.children:
            parent_lookup.setdefault(c, coll)
    return parent_lookup
