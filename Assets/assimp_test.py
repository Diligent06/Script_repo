import os
import shutil
import subprocess
import argparse

def convert_glb_to_obj(glb_path, output_dir):
    glb_path = os.path.abspath(glb_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    obj_path = os.path.join(output_dir, "model.obj")
    mtl_path = os.path.join(output_dir, "model.mtl")
    textures_dir = os.path.join(output_dir, "textures")
    os.makedirs(textures_dir, exist_ok=True)

    # Run Assimp export
    print(f"🔄 Converting {glb_path} to {obj_path}...")
    subprocess.run(["assimp", "export", glb_path, obj_path], check=True)

    # Move textures (e.g., .png, .jpg) to textures/
    for f in os.listdir(output_dir):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            shutil.move(os.path.join(output_dir, f), os.path.join(textures_dir, f))

    # Update MTL file paths
    if os.path.exists(mtl_path):
        with open(mtl_path, "r") as f:
            lines = f.readlines()
        with open(mtl_path, "w") as f:
            for line in lines:
                if line.strip().startswith("map_Kd"):
                    tex_name = line.strip().split(" ", 1)[1]
                    f.write(f"map_Kd textures/{os.path.basename(tex_name)}\n")
                else:
                    f.write(line)

    print("✅ Conversion complete.")
    print(f"🗂️ OBJ: {obj_path}")
    print(f"🎨 Textures: {textures_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", required=True, help="Path to input .glb file")
    parser.add_argument("--out", required=True, help="Output folder for .obj and textures")
    args = parser.parse_args()

    convert_glb_to_obj(args.glb, args.out)
