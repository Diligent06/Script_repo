import bpy
import os
from mathutils import Matrix, Euler
import json
from os.path import join
from scipy.spatial.transform import Rotation as R
from transforms3d.quaternions import mat2quat, quat2mat
import numpy as np


source_folder = './data/103997643_171030747_demo'
info_path = join(source_folder, "103997643_171030747_demo.scene_instance.json")


with open(info_path, 'r') as json_file:
    info = json.load(json_file)
json_file.close()

stage_instance = info["stage_instance"]
object_instance = info["object_instances"]

folder_path = './data/103997643_171030747_demo_usd'
output_source = './data/103997643_171030747_demo_usd_transfer'
for folder in os.listdir(folder_path):
    flag = False
    for item in object_instance:
        if item["template_name"] == folder:
            usd_path = join(join(folder_path, folder), f'{folder}.usd')
            translation = item["translation"]
            rotation = item["rotation"]
            scale = item["non_uniform_scale"]
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.wm.usd_import(filepath=usd_path)

            x, y, z = translation
            translation = [x, -z, y]
            w, x, y, z = rotation
            rotation = [x, y, z, w]
            r = R.from_quat(rotation)
            euler_rad = r.as_euler('xyz', degrees=False)

            print(f'raw euler_rad is {euler_rad}')
            euler_x, euler_y, euler_z = euler_rad
            euler_rad = [euler_x, -euler_z, euler_y]
            x, y, z = scale
            scale = [x, -z, y]
            print(f'transfered euler rad is {euler_rad}')
            # 应用旋转变换，确保它成为模型的一部分
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    obj.rotation_mode = 'XZY'
                    obj.location = tuple(translation)
                    import math
                    obj.rotation_euler = tuple(euler_rad)
                    obj.scale = tuple(scale)
                    
            bpy.ops.wm.usd_export(filepath=join(join(output_source, folder), f'{folder}.usd'))
            flag = True
            break

    if not flag:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.usd_import(filepath=join(join(folder_path, folder), f'{folder}.usd'))
        bpy.ops.wm.usd_export(filepath=join(join(output_source, folder), f'{folder}.usd'))
    
