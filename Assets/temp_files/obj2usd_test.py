import bpy
import os

def convert_obj_to_usd_blender(obj_path, usd_path):
    # 清除场景
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 导入 OBJ
    bpy.ops.wm.obj_import(filepath=obj_path,
                          directory=os.path.dirname(obj_path),
                          path_mode='RELATIVE'
                          )
    
    # 导出 USD
    bpy.ops.wm.usd_export(
        filepath=usd_path,
        export_animation=False,
        export_hair=False,
        export_uvmaps=True,
        export_normals=True,
        export_materials=True,
        export_textures=True
    )

# 使用前需要安装 blender 和 bpy 模块

convert_obj_to_usd_blender('./data/Mujoco_data/stage_obj/floor.obj', './test_floor.usd')