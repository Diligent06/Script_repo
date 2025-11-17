import json
import os
from os.path import join
import shutil

scene_config_file = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json"

raw_stage_folder = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/"
raw_object_folder = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/objects"

with open(scene_config_file, 'r') as json_file:
    json_text = json.load(json_file)
json_file.close()

stage = json_text["stage_instance"]
objects = json_text["object_instances"]

output_folder = "./data/103997643_171030747_demo"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

stage_folder = join(output_folder, 'stages')
object_folder = join(output_folder, 'objects')
static_folder = join(object_folder, 'static')
dynamic_folder = join(object_folder, 'dynamic')

os.makedirs(static_folder, exist_ok=True)
os.makedirs(dynamic_folder, exist_ok=True)
os.makedirs(stage_folder, exist_ok=True)

stage_name = stage['template_name']

if os.path.exists(join(raw_stage_folder, stage_name + '.glb')):
    shutil.copy(join(raw_stage_folder, stage_name + '.glb'), stage_folder)

for obj in objects:
    obj_name = obj['template_name']
    static = obj['motion_type']
    obj_path = None
    if static == 'STATIC':
        for dir in os.listdir(raw_object_folder):
            if dir == 'decomposed':
                continue
            if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                break
        if obj_path is not None:
            shutil.copy(obj_path, static_folder)
        else:
            print(f'{obj_name} can not found')
            pass
    else:
        for dir in os.listdir(raw_object_folder):
            if dir == 'decomposed':
                continue
            if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                break
        if obj_path is not None:
            shutil.copy(obj_path, dynamic_folder)
        else:
            print(f'{obj_name} can not found')
            pass

shutil.copy(scene_config_file, output_folder)




