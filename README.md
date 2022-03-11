# ezdxf_exporter
Download the latest version :

https://github.com/Gorgious56/blender_ezdxf_exporter/releases

This add-on uses ezdxf, pyparsing and typing_extensions python modules (shipped with the download)

It is supposed to be a replacement to the standard dxf exporter which lacks some features.

![image](https://user-images.githubusercontent.com/25156105/152991953-93ccb401-d33a-4ab6-a077-d3d92b4358c0.png)

Features:

- Save & Load Presets
- Filter exported objects or choose to put them on frozen layers if they are hidden
- Export Faces as MESH, 3DFace or Polyface
- Export Edges as Lines or Polylines
- Export Vertices as Points
- Export Curves as MESH objects (no support for splines yet)
- Export Text as Mtext or Text objects
- Linked objects are exported as blocks
- Put objects on layers depending on their material, data, collection, etc.
- Add a prefix or suffix to all layers
- Override for each exported type
- Export mesh, edges or points on sub layers
- Export materials as layers
- Set color ![image](https://user-images.githubusercontent.com/25156105/152992550-f38efabf-f419-4c5b-9fce-3479ef307cd8.png)
- Set Transparency
- Set File units
- Set unit multiple
- Set Length Display units
- Set Angle Display units
- Scale from 0, 0, 0
- Project along the scene camera, front, back, left, right, bottom or top coordinates
- Transform along X, Y, Z
