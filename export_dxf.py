import ezdxf
import bpy


def export_file(path):
    doc = ezdxf.new(dxfversion="R2010")

    collection_colors = bpy.context.preferences.themes[0].collection_color
    for coll in bpy.data.collections:
        new_layer = doc.layers.new(coll.name)

        color_tag = coll.color_tag
        if color_tag != 'NONE':
            col = [int(channel * 256)
                   for channel in collection_colors[int(color_tag[-2:])-1].color]
            new_layer.rgb = col

    msp = doc.modelspace()

    obj = bpy.context.object
    mesh = obj.data

    for e in mesh.edges:
        msp.add_line(
            mesh.vertices[e.vertices[0]].co,
            mesh.vertices[e.vertices[1]].co,
            dxfattribs={
                'layer': obj.users_collection[0].name
            })

    # Add entities to a layout by factory methods: layout.add_...()
    # msp.add_text(
    #    'Test',
    #    dxfattribs={
    #        'layer': 'TEXTLAYER'
    #    }).set_pos((0, 0.2), align='CENTER')

    doc.saveas(path)
