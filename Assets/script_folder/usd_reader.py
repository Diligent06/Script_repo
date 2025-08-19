import bpy
import os
from os.path import join

# 清空当前场景
bpy.ops.wm.read_factory_settings(use_empty=True)

input_usd_files = []

# USD 文件所在目录和输出路径
usd_file_path = './test_data/103997643_171030747_demo_usd'
for folder in os.listdir(usd_file_path):
    input_usd_files.append(join(join(usd_file_path, folder), f'{folder}.usd'))

output_usd_file = "./test_data_output/final.usd"

# 将所有 USD 文件导入 Blender
for usd_path in input_usd_files:
    if os.path.exists(usd_path):
        bpy.ops.wm.usd_import(filepath=usd_path)
    else:
        print(f"File not found: {usd_path}")

# 选择所有对象以便导出
for obj in bpy.data.objects:
    obj.select_set(True)

# 设置导出参数并导出合并后的 USD 文件
bpy.ops.wm.usd_export(
    filepath=output_usd_file,
    export_textures=True,            # 导出纹理（可选）
    export_materials=True,           # 导出材质
    selected_objects_only=False,     # 导出所有对象
    export_animation=False           # 是否导出动画（视情况而定）
)

print(f"Merged USD file saved to: {output_usd_file}")
