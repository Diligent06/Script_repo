import bpy
import os
from mathutils import Matrix, Euler
import json
from os.path import join
from scipy.spatial.transform import Rotation as R
import subprocess



def convert_glb(input_path, output_path):
    cmd = [
        "gltf-transform",
        "ktxdecompress",
        input_path,
        output_path
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        pass



# Set input/output directories
source_folder = './data/103997643_171030747_demo'
dynamic_folder = join(source_folder, 'objects/dynamic')
static_folder = join(source_folder, 'objects/static')
stage_folder = join(source_folder, 'stages')
candidate_folder = [dynamic_folder, static_folder, stage_folder]
info_path = join(source_folder, "103997643_171030747_demo.scene_instance.json")

with open(info_path, 'r') as json_file:
    info = json.load(json_file)
json_file.close()

stage_instance = info["stage_instance"]
object_instance = info["object_instances"]

output_folder = "./data/103997643_171030747_demo_usd/"
os.makedirs(output_folder, exist_ok=True)

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

for folder in candidate_folder:
    for file in os.listdir(folder):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        file_path = join(folder, file)
        convert_glb(file_path, file_path)
        file_name = file.split('.')[0]
        cur_output_folder = join(output_folder, file_name)

        bpy.ops.import_scene.gltf(filepath=file_path)

        bpy.ops.wm.usd_export(filepath=join(cur_output_folder, f'{file_name}.usd'))
        continue
        if folder == stage_folder:
            bpy.ops.wm.usd_export(filepath=join(cur_output_folder, f'{file_name}.usd'))
            continue
        
        
        translation = [0, 0, 0]
        rotation = [0, 0, 0]
        scale = [1, 1, 1]
        
        for item in object_instance:
            if item["template_name"] == file_name:
                translation = item["translation"]
                rotation = item["rotation"]
                scale = item["non_uniform_scale"]
                
                break
        
        x, y, z = translation
        translation = [x, -z, y]

        w, x, y, z = rotation
        rotation = [x, y, z, w]
        r = R.from_quat(rotation)
        euler_rad = r.as_euler('xyz', degrees=False)
        
        x, y, z = scale
        scale = [x, -z, y]

        # 应用旋转变换，确保它成为模型的一部分
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.rotation_mode = 'XZY'
                obj.location = tuple(translation)
                obj.rotation_euler = tuple(euler_rad)
                obj.scale = tuple(scale)

        bpy.ops.wm.usd_export(filepath=join(cur_output_folder, f'{file_name}.usd'))





