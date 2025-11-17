import pygltflib
from PIL import Image
import numpy as np
import os
import bpy
import base64


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
        print(suffix)
    image_file.close()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    image = pygltflib.Image(uri=f"data:image/{suffix};base64,{image_base64}")
    # image = pygltflib.Image(uri=image_filename)
    gltf.images.clear()
    texture = pygltflib.Texture(source=len(gltf.images))
    gltf.textures.clear()
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

if __name__ == '__main__':
    texture_path = "/media/diligent/BEA6-BBCE/final_directory/visuals.101/textures/houseplant_surface_6_24_LeavesSetup_Leaves_AlbedoTransparency.png"
    glb_path = "/home/diligent/Desktop/habitat-sim/data/habitat_temp/objects/static/visuals.101.glb"
    # save_path = "/media/diligent/BEA6-BBCE/final_directory/visuals.085/temp.glb"
    add_texture_to_glb(glb_path, texture_path, glb_path)
    pass