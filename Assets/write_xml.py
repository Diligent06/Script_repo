import argparse
import os
from os.path import join
import json
from convert import Converter

my_converter = Converter()

template_obj = '\t\t<texture name="OBJ_texture" type="2d" file="FOLDER/OBJ.png"/>\n\t\t<material name="OBJ_material" texture="OBJ_texture" specular="0.3"/>\n\t\t<mesh name="OBJ" file="FOLDER/OBJ.obj" />\n'
template_geo = '\t\t<geom name="OBJ" type="mesh" mesh="OBJ" material="OBJ_material"/>\n'

template_no_texture_obj = '\t\t<mesh name="OBJ" file="FOLDER/OBJ.obj" />\n'
template_no_texture_geo = '\t\t<geom name="OBJ" type="mesh" mesh="OBJ"/>\n'

geo_template = '<geom name="OBJ" type="mesh" mesh="OBJ" material="OBJ_mtl"/>'
mesh_template = '<mesh name="OBJ" file="FOLDER/OBJ.obj" />'
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--obj_folder",
        default='./data/Mujoco_data/',
        type=str
    )
    parser.add_argument(
        "--output_path",
        default='./data/Mujoco_data/scene.xml',
        type=str
    )
    args = parser.parse_args()

    dynamic_folder = join(args.obj_folder, 'dynamic_obj')
    stage_folder = join(args.obj_folder, 'stage_obj')
    static_folder = join(args.obj_folder, 'static_obj')

    obj_list = []
    geo_list = []
    for file in os.listdir(dynamic_folder):
        folder_name = dynamic_folder.split('/')[-1]
        if file.endswith('.obj'):
            obj_name = file.split('.')[0]
            if os.path.exists(join(dynamic_folder, obj_name + '.json')):
                with open(join(dynamic_folder, obj_name + '.json'), 'r') as json_file:
                    text = json.load(json_file)[f'{obj_name}_mtl']
                json_file.close()
            obj_list.append(text + '\n' + mesh_template.replace('OBJ', obj_name).replace('FOLDER', f'./{folder_name}'))
            geo = geo_template.replace('OBJ', obj_name)
            geo_list.append(geo)
        
    for file in os.listdir(stage_folder):
        folder_name = stage_folder.split('/')[-1]
        if file.endswith('.obj'):
            obj_name = file.split('.')[0]
            if os.path.exists(join(stage_folder, obj_name + '.json')):
                with open(join(stage_folder, obj_name + '.json'), 'r') as json_file:
                    text = json.load(json_file)[f'{obj_name}_mtl']
                json_file.close()
            obj_list.append(text + '\n' + mesh_template.replace('OBJ', obj_name).replace('FOLDER', f'./{folder_name}'))
            geo = geo_template.replace('OBJ', obj_name)
            geo_list.append(geo)
    
    for file in os.listdir(static_folder):
        folder_name = static_folder.split('/')[-1]
        if file.endswith('.obj'):
            obj_name = file.split('.')[0]
            if os.path.exists(join(static_folder, obj_name + '.json')):
                with open(join(static_folder, obj_name + '.json'), 'r') as json_file:
                    text = json.load(json_file)[f'{obj_name}_mtl']
                json_file.close()
            obj_list.append(text + '\n' + mesh_template.replace('OBJ', obj_name).replace('FOLDER', f'./{folder_name}'))
            geo = geo_template.replace('OBJ', obj_name)
            geo_list.append(geo)
    
    with open(args.output_path, 'w') as xml_file:
        xml_file.write('<mujoco model="minimal">\n\t<asset>\n')
        for obj in obj_list:
            xml_file.write(obj)
        xml_file.write('\t</asset>\n\t<worldbody>\n')
        for geo in geo_list:
            xml_file.write(geo)
        xml_file.write('\t</worldbody>\n</mujoco>')

    xml_file.close()
    my_converter.pretty_print_xml(args.output_path)
        

