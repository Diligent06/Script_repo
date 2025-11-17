import os
import subprocess
import sys

glb_file = "./data/assets/stages/floor.glb"
unpacked_dir = "./unpack_dir"
obj_file = "./unpack_dir/output.obj"

# 1. Unpack .glb to .gltf + textures
subprocess.run([
    "gltf-transform", "unpack",
    glb_file,
    unpacked_dir
], check=True)

# 2. Convert .gltf to .obj using assimp
unpacked_gltf = os.path.join(unpacked_dir, "scene.gltf")
subprocess.run([
    "assimp", "export",
    unpacked_gltf,
    obj_file
], check=True)

print("✅ Conversion complete.")
