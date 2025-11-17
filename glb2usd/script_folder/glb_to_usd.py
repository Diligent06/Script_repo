import bpy
import sys
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
        print("转换成功！")
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("转换失败:", e)
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)

# # Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Path to your .glb file
glb_path = 'data/103997643_171030747_demo/stages/103997643_171030747.glb'
convert_glb(glb_path, glb_path)
# Path to output .usd file
usd_path = "./103997643_171030747.usd"

# Import GLB
bpy.ops.import_scene.gltf(filepath=glb_path)

# Export to USD
bpy.ops.wm.usd_export(filepath=usd_path)

# from convert import Converter

# my_converter = Converter()
# glb_path = 'data/103997643_171030747_demo/stages/103997643_171030747.glb'
# my_converter.convert_glb_to_obj(glb_path, obj_path='./obj_folder')
