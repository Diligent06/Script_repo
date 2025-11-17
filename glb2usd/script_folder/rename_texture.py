import os
import shutil
from os.path import join

def rename_textures_and_update_usd(usd_file_path):
    from pxr import Usd, UsdShade, Sdf

    usd_dir = os.path.dirname(usd_file_path)
    usd_name = os.path.splitext(os.path.basename(usd_file_path))[0]
    prefix = usd_file_path.split('/')[-1].split('.')[0]
    # 打开 usd 文件
    stage = Usd.Stage.Open(usd_file_path)
    file_dict = {}
    for prim in stage.Traverse():
        if prim.IsA(UsdShade.Shader):
            shader = UsdShade.Shader(prim)
            
            # 检查是否是纹理 shader（类型通常为 "UsdPreviewSurface" 或 "UsdUVTexture"）
            if shader.GetIdAttr().Get() == "UsdUVTexture":
                # 获取纹理文件输入
                file_input = shader.GetInput("file")
                if file_input:
                    old_path = file_input.Get()
                    if isinstance(old_path, Sdf.AssetPath):
                        old_asset_path = old_path.path
                        if old_asset_path in file_dict.keys():
                            # print('use dict')
                            file_input.Set(Sdf.AssetPath(file_dict[old_asset_path]))
                        filename = os.path.basename(old_asset_path)
                        new_filename = prefix + '_' +  filename
                        new_asset_path = os.path.join(os.path.dirname(old_asset_path), new_filename)
                        # print(new_asset_path)
                        # print(old_asset_path)
                        # 设置新的纹理路径
                        file_input.Set(Sdf.AssetPath(new_asset_path))
                        old_file_name = old_asset_path.split('/')[-1]
                        old_rename_path = join(os.path.dirname(usd_file_path), f'textures/{old_file_name}')
                        new_rename_path = join(os.path.dirname(usd_file_path), f'textures/{new_filename}')
                        
                        if os.path.exists(old_rename_path):
                            os.rename(old_rename_path, new_rename_path)
                            file_dict.update({old_asset_path: new_asset_path})
                        print(f"Changed texture: {old_asset_path} → {new_asset_path}")

    # 保存修改后的 usd 文件
    stage.GetRootLayer().Save()

usd_folder = './data/103997643_171030747_demo_usd_transfer/'

for usd in os.listdir(usd_folder):
    usd_file = join(join(usd_folder, usd), f'{usd}.usd')
    rename_textures_and_update_usd(usd_file)