from .shared_properties import dxf_mesh_type

def create_mesh(mesh_type):
    if mesh_type == dxf_mesh_type.FACES3D:
        return create_mesh_3dfaces
    elif mesh_type == dxf_mesh_type.POLYFACE:
        return create_mesh_polyface
    elif mesh_type == dxf_mesh_type.POLYLINES:
        return create_mesh_polylines
    elif mesh_type == dxf_mesh_type.LINES:
        return create_mesh_lines
    elif mesh_type == dxf_mesh_type.POINTS:
        return create_mesh_points

def create_mesh_points(msp, mesh, matrix, dxfattribs):
    for v in mesh.vertices:
        msp.add_point(
            matrix @ v.co,
            dxfattribs=dxfattribs)

def create_mesh_lines(msp, mesh, matrix, dxfattribs):
    for e in mesh.edges:
        msp.add_line(
            matrix @ mesh.vertices[e.vertices[0]].co,
            matrix @ mesh.vertices[e.vertices[1]].co,
            dxfattribs=dxfattribs)

def create_mesh_polylines(msp, mesh, matrix, dxfattribs):
    for e in mesh.edges:
        msp.add_polyline3d(
            (
                matrix @ mesh.vertices[e.vertices[0]].co,
                matrix @ mesh.vertices[e.vertices[1]].co,
            ),
            dxfattribs=dxfattribs)

def create_mesh_polyface(msp, mesh, matrix, dxfattribs):        
    polyface = msp.add_polyface(dxfattribs=dxfattribs)
    polyface.append_faces(
        [[matrix @ mesh.vertices[v].co for v in f.vertices] for f in mesh.polygons],
        dxfattribs=dxfattribs)
    polyface.optimize()

def create_mesh_3dfaces(msp, mesh, matrix, dxfattribs):           
    for f in mesh.polygons:
        msp.add_3dface(
            [matrix @ mesh.vertices[v].co for v in f.vertices],
            dxfattribs=dxfattribs)