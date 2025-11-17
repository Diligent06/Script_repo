import pygltflib
from PIL import Image
import numpy as np
import os
import bpy
import base64
from pxr import Usd, UsdShade

def add_texture_to_glb(glb_path, texture_path, save_path):
    # 加载 GLB 文件
    gltf = pygltflib.GLTF2().load(glb_path)

    # 读取纹理图像
    texture_image = Image.open(texture_path)
    texture_image = texture_image.convert('RGB')
    image_data = np.array(texture_image)
    
    # 保存图像到文件
    image_filename = os.path.basename(texture_path)
    image_path = os.path.join(os.path.dirname(glb_path), image_filename)
    # texture_image.save(image_path)

    # 创建新的图像和纹理
    with open(texture_path, 'rb') as image_file:
        image_data = image_file.read()
        suffix = texture_path.split('.')[-1]
    image_file.close()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    image = pygltflib.Image(uri=f"data:image/{suffix};base64,{image_base64}")
    # image = pygltflib.Image(uri=image_filename)
    texture = pygltflib.Texture(source=len(gltf.images))

    # 添加图像和纹理到 GLTF 数据
    gltf.images.append(image)
    gltf.textures.append(texture)

    # 处理材质以使用新纹理
    for material in gltf.materials:
        if material.pbrMetallicRoughness:
            material.pbrMetallicRoughness.baseColorTexture = pygltflib.TextureInfo(index=len(gltf.textures) - 1)
    
    # 将 GLTF 文件转换为 GLB 文件
    # gltf.convert_glb()
    gltf.save(save_path)

def convert_usd_to_glb(usd_file_path, glb_file_path):
    # 清空当前场景
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 导入 USD 文件
    bpy.ops.wm.usd_import(filepath=usd_file_path)
    
    # 导出为 GLB 文件
    bpy.ops.export_scene.gltf(
        filepath=glb_file_path,
        export_format='GLB',  # 选择 GLB 格式
        export_texture_dir='AUTO',  # 自动管理纹理
        export_materials='EXPORT'  # 导出材质
    )
def get_texture_file_name(stage):
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Material):
            for children in prim.GetAllChildren():
                attr = children.GetAttribute('inputs:diffuse_texture')
                temp = str(attr.Get())
                temp = temp.split('/')[-1][0:-1]
                return temp
    return None
if __name__ == '__main__':
    directory_path = "./final_directory"
    glb_output_path = "./final_glb"
    os.makedirs(glb_output_path, exist_ok=True)
    for dir in os.listdir(directory_path):
        usd_file_path = os.path.join(directory_path, f'{dir}/{dir}.usd')
        glb_file_path = os.path.join(glb_output_path, f"{dir}.glb")
        convert_usd_to_glb(usd_file_path, glb_file_path)
        if os.path.exists(os.path.join(directory_path, f"{dir}/textures")):
            images = os.listdir(os.path.join(directory_path, f'{dir}/textures'))
            stage = Usd.Stage.Open(usd_file_path)
            image_name = get_texture_file_name(stage)
            if image_name != None and os.path.exists(os.path.join(directory_path, f'{dir}/textures/{image_name}')):
                pass
            else:
                not_find = not_find + 1
                image_name = images[-1]
            # print(image_name)
            texture_path = os.path.join(directory_path, f'{dir}/textures/{image_name}')
            add_texture_to_glb(glb_file_path, texture_path, glb_file_path)
