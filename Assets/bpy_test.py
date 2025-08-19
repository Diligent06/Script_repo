import bpy
import sys
import os

# -------- Parameters --------
glb_path = "./data/103997643_171030747_demo/103997643_171030747_demo/objects/static/0b0e6df6479ffd5c48f58de1330e7f2ab1248620.glb"
obj_path = "./bpy_test_obj.obj"

# -------- Start Fresh Scene --------
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------- Import GLB --------
bpy.ops.import_scene.gltf(filepath=glb_path)

# -------- Export OBJ --------
bpy.ops.wm.obj_export(
    filepath=obj_path,
    path_mode='COPY',           # Copy textures
    forward_axis='Y',
    up_axis='Z',
    export_selected_objects=True,
    export_materials=True
)

print("✅ Export complete:", obj_path)

