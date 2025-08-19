from urdfpy import URDF
from convert import Converter
import os
from os.path import join
from urdfpy import URDF
from lxml import etree as ET


my_convert = Converter()




my_convert.fix_urdf_limits('./data/assets/urdfs/8867/8867.urdf')
my_convert.pretty_print_xml('./data/assets/urdfs/8867/8867.urdf')
robot = URDF.load('./data/assets/urdfs/8867/8867.urdf')

links = [link.name for link in robot.links]
obj_folder = './data/assets/urdfs/8867/textured_objs'
files = os.listdir(obj_folder)

output_folder = './test_output/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for link in links:
    if f'{link}.obj' in files:
        my_convert.split_obj_by_material(join(obj_folder, f'{link}.obj'), join(output_folder, link))

        my_convert.material_decompose(join(obj_folder, f'{link}.mtl'), join(output_folder, link), path_prefix=link, copy_texture=True)

my_convert.process_json('./test_output/link_1/link_1.json', 'none')


# def urdf_to_mjcf(urdf_path, mjcf_output_path):
#     robot = URDF.load(urdf_path)

#     mjcf_root = ET.Element("mujoco", model=robot.name)
#     worldbody = ET.SubElement(mjcf_root, "worldbody")
#     assets = ET.SubElement(mjcf_root, "asset")
#     default = ET.SubElement(mjcf_root, "default")
#     ET.SubElement(default, "joint", limited="true", damping="1")

#     for link in robot.links:
#         if link.visuals:
#             for visual in link.visuals:
#                 pos = " ".join(map(str, visual.origin[:3]))
#                 geom_type = "mesh" if visual.geometry.mesh else "sphere"
#                 mesh_name = link.name + "_mesh"
#                 if visual.geometry.mesh:
#                     ET.SubElement(assets, "mesh", name=mesh_name, file=visual.geometry.mesh.filename)
#                 ET.SubElement(worldbody, "body", name=link.name, pos=pos)
#                 ET.SubElement(worldbody[-1], "geom", type=geom_type, mesh=mesh_name, rgba="0.8 0.3 0.3 1")

#     for joint in robot.joints:
#         parent = joint.parent
#         child = joint.child
#         pos = " ".join(map(str, joint.origin[:3]))
#         axis = " ".join(map(str, joint.axis)) if joint.axis is not None else "1 0 0"
#         joint_type = joint.joint_type if joint.joint_type != "continuous" else "hinge"

#         body_elem = worldbody.find(f".//body[@name='{child}']")
#         if body_elem is not None:
#             ET.SubElement(body_elem, "joint", name=joint.name, type=joint_type, axis=axis, pos=pos)

#     # Save to file
#     tree = ET.ElementTree(mjcf_root)
#     tree.write(mjcf_output_path, pretty_print=True, xml_declaration=True, encoding='utf-8')
#     print(f"[DONE] MJCF saved to {mjcf_output_path}")

# # Example usage
# urdf_to_mjcf('./data/assets/urdfs/8867/8867.urdf', './output_robot.xml')
