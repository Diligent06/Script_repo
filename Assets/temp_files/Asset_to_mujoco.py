import trimesh
import os
import shutil
from os.path import join
import argparse
from convert import Converter
import aspose
from aspose.threed import *
from PIL import Image
# from aspose.threed.utilities import TrialException

# TrialException.suppress_trial_exception = True
# TrialException.SuppressTrialException = True

my_converter = Converter()

def convert_glb_to_obj(glb_path, obj_path):
    # 加载 GLB
    scene = Scene.from_file(glb_path)
    options = aspose.threed.formats.ObjSaveOptions()
    options.enable_materials = True
    options.export_textures = True

    # 暂时导出到默认文件
    temp_obj_path = obj_path
    scene.save(temp_obj_path, options)

    base_dir = os.path.dirname(obj_path)
    # 查找生成的 .mtl 文件
    base_name = obj_path.split('/')[-1].split('.')[0]
    material_name = f'{base_name}.mtl'

    with open(join(base_dir, material_name), 'r') as f:
        lines = f.readlines()

    Kd_file_name = None
    with open(join(base_dir, material_name), 'w') as f:
        for line in lines:
            if line.startswith('#'):
                continue
            else:
                line = line.replace('\t', '')
                if line == "\n":
                    continue
                else:
                    if line.startswith('map_Kd'):
                        Kd_file_name = line.split(' ')[-1]
                        if Kd_file_name[-1] == '\n':
                            Kd_file_name = Kd_file_name[:-1]
                        ext = Kd_file_name.split('.')[-1]
                        ext = 'png'
                        line = line.split(' ')[0] + f' {base_name}.{ext}\n'
                    elif line.startswith('newmtl'):
                        line = f'newmtl {base_name}_mtl\n'
                    else:
                        if line.split(' ')[-1].endswith('.png\n') or line.split(' ')[-1].endswith('.jpg\n'):
                            file_name = line.split(' ')[-1]
                            if os.path.exists(join(base_dir, file_name)):
                                os.remove(join(base_dir, file_name))
                            continue
                    f.write(line)
    
    if Kd_file_name is not None:
        raw_file_path = join(base_dir, Kd_file_name)
        ext = Kd_file_name.split('.')[-1]
        if ext == 'jpg':
            img = Image.open(raw_file_path)
            target_file = Kd_file_name.split('.')[0] + '.png'
            img.save(join(base_dir, target_file))
            os.remove(raw_file_path)
            raw_file_path = join(base_dir, target_file)
        ext = 'png'
        target_file_path = join(base_dir, f'{base_name}.{ext}')
        os.rename(raw_file_path, target_file_path)
    my_converter.material_decompose(join(os.path.dirname(obj_path), material_name), os.path.dirname(obj_path), obj_path.split('/')[-2])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--glb_folder_path",
        default=join("./data/assets/"),
        type=str
    )
    parser.add_argument(
        "--output_folder",
        default=join("./data/"),
        type=str
    )
    parser.add_argument(
        "--dataset_name",
        default="Mujoco_data_hssd",
        type=str,
        help='Name of dataset'
    )
    args = parser.parse_args()

    dynamic_obj_path = join(join(args.output_folder, args.dataset_name), 'dynamic_obj')
    static_obj_path = join(join(args.output_folder, args.dataset_name), 'static_obj')
    stage_obj_path = join(join(args.output_folder, args.dataset_name), 'stage_obj')
    os.makedirs(dynamic_obj_path, exist_ok=True)
    os.makedirs(static_obj_path, exist_ok=True)
    os.makedirs(stage_obj_path, exist_ok=True)

    dynamic_glb_path = join(args.glb_folder_path, 'objects/dynamic')
    for dynamic_glb in os.listdir(dynamic_glb_path):
        convert_glb_to_obj(join(dynamic_glb_path, dynamic_glb), join(dynamic_obj_path, dynamic_glb.split('.')[0] + '.obj'))

    static_glb_path = join(args.glb_folder_path, 'objects/static')
    for static_glb in os.listdir(static_glb_path):
        convert_glb_to_obj(join(static_glb_path, static_glb), join(static_obj_path, static_glb.split('.')[0] + '.obj'))

    stage_glb_path = join(args.glb_folder_path, 'stages')
    for stage_glb in os.listdir(stage_glb_path):
        convert_glb_to_obj(join(stage_glb_path, stage_glb), join(stage_obj_path, stage_glb.split('.')[0] + '.obj'))

    

    
    
