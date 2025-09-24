import os
from os.path import join
import json
from collections import defaultdict
from pygltflib import GLTF2
import base64
import mimetypes
import xml.etree.ElementTree as ET
import xml.dom.minidom
import shutil
from PIL import Image


class Converter():
    def __init__(self):
        pass

    def material_decompose(self, file_path, output_folder="", path_prefix="", copy_texture=False):
        with open(file_path, "r") as f:
            mtl_text = f.read()

        prefix = file_path.split('/')[-1].split('.')[0]

        materials = {}
        blocks = self.parse_mtl_blocks(mtl_text)

        file_name = file_path.split('/')[-1].split('.')[0]
        file_dir = os.path.dirname(file_path)
        for block in blocks:
            mtl_name = block.split('\n')[0].split(' ')[-1]
            with open(join(file_dir, file_name + '_' + mtl_name + '.mtl'), 'w') as file:
                file.write(block)
            file.close()
        for i, block in enumerate(blocks):
            mat = self.parse_mtl_block(block)
            if mat["texture"] and copy_texture:
                if os.path.exists(join(os.path.dirname(file_path), mat["texture"])):
                    img = Image.open(join(os.path.dirname(file_path), mat["texture"]))
                    output_name = mat["name"].split('/')[-1]
                    img.save(join(output_folder, f"{output_name}.png"))
            mjcf = self.generate_mjcf_material(mat, path_prefix)
            if mat['name'] != '':
                materials[mat['name'].replace('.', '_')] = mjcf
        if output_folder != "":
            with open(join(output_folder, f'{prefix}.json'), 'w') as json_file:
                json.dump(materials, json_file, indent=4)
            json_file.close()
    
    def write_mtl_json(self, file_path, output_folder, path_prefix="", file_name=""):
        with open(file_path, "r") as f:
            mtl_text = f.read()
        blocks = self.parse_mtl_blocks(mtl_text)
        prefix = file_path.split('/')[-1].split('.')[0]

        materials = {}
        for i, block in enumerate(blocks):
            mat = self.parse_mtl_block(block)
            mjcf = self.generate_mjcf_material(mat, path_prefix, file_name)
            if mat['name'] != '':
                materials[mat['name'].replace('.', '_')] = mjcf
        if output_folder != "":
            with open(join(output_folder, f'{prefix}.json'), 'w') as json_file:
                json.dump(materials, json_file, indent=4)
            json_file.close()

    def split_obj_by_material(self, obj_path, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(obj_path, 'r') as f:
            lines = f.readlines()

        header = []
        material_faces = defaultdict(list)
        current_material = None

        for line in lines:
            if line.startswith('mtllib') or line.startswith('o ') or line.startswith('v ') or line.startswith('vn ') or line.startswith('vt '):
                header.append(line)
            elif line.startswith('usemtl'):
                current_material = line.strip().split()[1]
                current_material = current_material.replace('.', '_')
            elif line.startswith('f '):
                if current_material:
                    material_faces[current_material].append(line)
            else:
                header.append(line)

        base_name = obj_path.split('/')[-1].split('.')[0]
        for mat, faces in material_faces.items():
            output_file = f"{base_name}_{mat}.obj"
            with open(join(output_folder, output_file), 'w') as out:
                for h in header:
                    out.write(h)
                out.write(f"usemtl {mat}\n")
                for face in faces:
                    out.write(face)
                       
    def extract_embedded_textures(self, glb_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        gltf = GLTF2().load(glb_path)

        with open(glb_path, 'rb') as f:
            binary_blob = f.read()

        for i, image in enumerate(gltf.images):
            # Case 1: data URI
            if image.uri and image.uri.startswith("data:"):
                print(f"[INFO] Texture {i} is a base64-encoded URI.")
                header, base64_data = image.uri.split(",", 1)
                ext = "jpg" if "jpeg" in header else "png"
                data = base64.b64decode(base64_data)

            # Case 2: Embedded binary buffer
            elif image.bufferView is not None:
                print(f"[INFO] Texture {i} is embedded in binary bufferView.")
                buffer_view = gltf.bufferViews[image.bufferView]
                offset = buffer_view.byteOffset or 0
                length = buffer_view.byteLength
                buffer_idx = buffer_view.buffer

                buffer_data = gltf.buffers[buffer_idx]
                if buffer_data.uri is None:
                    # Buffer is embedded
                    buffer_offset = gltf.header.size
                    start = offset + buffer_offset
                    data = binary_blob[start:start + length]
                else:
                    raise NotImplementedError("External buffer file not handled in this example.")

                # Guess extension based on MIME
                mime = image.mimeType or 'image/png'
                ext = mimetypes.guess_extension(mime).lstrip(".") or "png"

            else:
                print(f"[WARN] Texture {i} has no extractable data.")
                continue

            # Save texture to disk
            filename = f"texture_{i}.{ext}"
            path = os.path.join(output_dir, filename)
            with open(path, "wb") as f:
                f.write(data)
            print(f"[✔] Saved embedded texture: {path}")

    def pretty_print_xml(self, input_path, output_path=None, info=False):
        with open(input_path, 'r') as file:
            raw_xml = file.read()
        
        dom = xml.dom.minidom.parseString(raw_xml)
        pretty_xml = dom.toprettyxml(indent="  ")
        pretty_xml = "\n".join([line for line in pretty_xml.split('\n') if line.strip() != ""])

        output_path = output_path or input_path
        with open(output_path, 'w') as file:
            file.write(pretty_xml)
        if info:
            print(f"[DONE] Pretty-printed XML saved to: {output_path}")

    def fix_urdf_limits(self, urdf_path, output_path=None, default_effort="1.0", default_velocity="1.0", info=False):
        tree = ET.parse(urdf_path)
        root = tree.getroot()

        for joint in root.findall('joint'):
            joint_name = joint.attrib.get('name', '')
            limit = joint.find('limit')

            if limit is None:
                # 完全缺失 limit 节点，创建一个新的
                limit = ET.SubElement(joint, 'limit')
                limit.set('effort', default_effort)
                limit.set('velocity', default_velocity)
                if info:
                    print(f"[INFO] Added new <limit> to joint '{joint_name}'")
            else:
                # 补齐缺失的属性
                if 'effort' not in limit.attrib:
                    limit.set('effort', default_effort)
                    if info:
                        print(f"[INFO] Added missing effort to joint '{joint_name}'")
                if 'velocity' not in limit.attrib:
                    limit.set('velocity', default_velocity)
                    if info:
                        print(f"[INFO] Added missing velocity to joint '{joint_name}'")

        # 写入结果
        output_path = output_path or urdf_path
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        if info:
            print(f"[DONE] Fixed URDF saved to: {output_path}")

    def parse_mtl_blocks(self, mtl_content):
        materials = []
        current_block = []

        for line in mtl_content.splitlines():
            line = line.strip()
            if line.startswith("newmtl"):
                if current_block:
                    if current_block[0].startswith("newmtl"):
                        materials.append("\n".join(current_block))
                    current_block = []
            if line:  # 跳过空行
                current_block.append(line)

        if current_block:
            materials.append("\n".join(current_block))

        return materials

    def parse_mtl_block(self, block):
        lines = block.splitlines()
        material = {
            "name": "",
            "rgba": [1, 1, 1, 1],
            "specular": 0.2,
            "texture": None
        }

        for line in lines:
            tokens = line.split()
            if not tokens:
                continue
            if tokens[0] == "newmtl":
                material["name"] = tokens[1]
            elif tokens[0] in ("Ka", "Kd"):  # 使用 Kd 为主色
                r, g, b = map(float, tokens[1:])
                material["rgba"] = [r, g, b, 1.0]
            elif tokens[0] == "Ks":
                material["specular"] = sum(map(float, tokens[1:])) / 3.0
            elif tokens[0] == "map_Kd":
                material["texture"] = tokens[1]
        return material

    def generate_mjcf_material(self, material, prefix="", file_name=""):
        name = material["name"].split('/')[-1]
        r, g, b, a = material["rgba"]
        specular = material["specular"]

        xml_parts = []
        if material["texture"]:
            texture_name = material["texture"].split('/')[-1]
            file_path = join(join('./', prefix), texture_name)
            if file_name != "":
                xml_parts.append(f'<texture name="{file_name}_{name}_tex" type="2d" file="{file_path}"/>')
                xml_parts.append(
                    f'<material name="{file_name}_{name}_mtl" texture="{file_name}_{name}_tex" specular="{specular}" rgba="{r} {g} {b} {a}"/>'
                )
            else:
                xml_parts.append(f'<texture name="{name}_tex" type="2d" file="{file_path}"/>')
                xml_parts.append(
                    f'<material name="{name}_mtl" texture="{name}_tex" specular="{specular}" rgba="{r} {g} {b} {a}"/>'
                )
        else:
            if file_name != "":
                xml_parts.append(
                    f'<material name="{file_name}_{name}_mtl" specular="{specular}" rgba="{r} {g} {b} {a}"/>'
                )
            else:
                xml_parts.append(
                    f'<material name="{name}_mtl" specular="{specular}" rgba="{r} {g} {b} {a}"/>'
                )
        return "\n".join(xml_parts)
    
    def process_json(self, json_path, output_json_path):
        import re

        pattern_element = r'<(.*?)/>'

        with open(json_path, 'r') as json_file:
            json_text = json.load(json_file)
        json_file.close()

        for key in json_text.keys():
            element = {}
            matches = re.findall(r'(\w+)="(.*?)"', json_text[key])
            print(matches)
            # matches = re.findall(pattern_element, json_text[key], re.DOTALL)
            # for match in matches:
            #     splited_match = match.split(' ')
            #     match_name = splited_match[0]
            #     match_value = {}
            #     print('splited_match')
            #     print(splited_match)
            #     for attr in splited_match[1:]:
            #         attr_list = attr.split('=')
            #         print(attr_list)
            #         attr_name = attr_list[0]
            #         attr_value = attr_list[1]
            #         match_value.update({attr_name: attr_value})
            #     element.update({match_name: match_value})
            # print(element)                    

    def convert_glb_to_obj(self, glb_path, obj_path):
        # 加载 GLB
        import aspose.threed
        
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
        self.material_decompose(join(os.path.dirname(obj_path), material_name), os.path.dirname(obj_path), obj_path.split('/')[-2])

    def decompress_glb(self, input_path, output_path):
        import subprocess
        cmd = [
            "gltf-transform",
            "ktxdecompress",
            input_path,
            output_path
        ]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            print('throw out exception')
            pass

    
class GLB2USD():
    def __init__(self):
        pass

    def convert(self, source_path, output_folder, scene_config_file):
        scene_name = scene_config_file.split('/')[-1].split('.')[0]
        if os.path.exists(join(output_folder, f'{scene_name}')):
            return
        self.copy_scene(scene_config_file, source_path, join(output_folder, f'{scene_name}'))
        info_path = join(join(output_folder, f'{scene_name}'), f'{scene_name}.scene_instance.json')
        self.convert_glbs_usds(join(output_folder, f'{scene_name}'), join(output_folder, f'{scene_name}_usd'))
        self.transform_usd(info_path, join(output_folder, f'{scene_name}_usd'), join(output_folder, f'{scene_name}_usd_transfer'))
        self.modify_usds_texture(join(output_folder, f'{scene_name}_usd_transfer'))
        self.merge_all_usds(join(output_folder, f'{scene_name}_usd_transfer'), join(join(output_folder, f'{scene_name}_final'), f'{scene_name}.usd'))
    
    def convert_wo_copy(self, source_path, output_folder, scene_name):
        self.convert_glbs_usds(source_path, join(output_folder, f'{scene_name}_usd'))
        self.merge_all_usds(join(output_folder, f'{scene_name}_usd'), join(join(output_folder, f'{scene_name}_final'), f'{scene_name}.usd'))
    
    def copy_scene(self, scene_config_file, source_folder, output_folder):
        # scene_config_file = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json"
        # raw_object_folder = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/objects"
        # raw_stage_folder = "/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/"
        # output_folder = "./data/103997643_171030747_demo"

        if os.path.exists(output_folder):
            return

        raw_stage_folder = join(source_folder, "stages")
        raw_object_folder = join(source_folder, "objects")

        with open(scene_config_file, 'r') as json_file:
            json_text = json.load(json_file)
        json_file.close()

        stage = json_text["stage_instance"]
        objects = json_text["object_instances"]

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        stage_folder = join(output_folder, 'stages')
        object_folder = join(output_folder, 'objects')
        static_folder = join(object_folder, 'static')
        dynamic_folder = join(object_folder, 'dynamic')

        os.makedirs(static_folder, exist_ok=True)
        os.makedirs(dynamic_folder, exist_ok=True)
        os.makedirs(stage_folder, exist_ok=True)

        stage_name = stage['template_name'].split('/')[-1]

        if os.path.exists(join(raw_stage_folder, stage_name + '.glb')):
            shutil.copy(join(raw_stage_folder, stage_name + '.glb'), stage_folder)

        for obj in objects:
            obj_name = obj['template_name']
            static = obj['motion_type']
            obj_path = None
            if static == 'STATIC':
                for dir in os.listdir(raw_object_folder):
                    if dir == 'decomposed':
                        continue
                    if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                        obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                        break
                if obj_path is not None:
                    shutil.copy(obj_path, static_folder)
                else:
                    print(f'{obj_name} can not found')
                    pass
            else:
                for dir in os.listdir(raw_object_folder):
                    if dir == 'decomposed':
                        continue
                    if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                        obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                        break
                if obj_path is not None:
                    shutil.copy(obj_path, dynamic_folder)
                else:
                    print(f'{obj_name} can not found')
                    pass

        shutil.copy(scene_config_file, output_folder)

    def convert_glbs_usds(self, source_folder, output_folder):
        import bpy

        dynamic_folder = join(source_folder, 'objects/dynamic')
        static_folder = join(source_folder, 'objects/static')
        stage_folder = join(source_folder, 'stages')
        candidate_folder = [dynamic_folder, static_folder, stage_folder]
     
        os.makedirs(output_folder, exist_ok=True)

        for folder in candidate_folder:
            for file in os.listdir(folder):
                bpy.ops.wm.read_factory_settings(use_empty=True)
                file_path = join(folder, file)
                self.decompress_glb(file_path, file_path)
                file_name = file.split('.')[0]
                cur_output_folder = join(output_folder, file_name)
        
                bpy.ops.import_scene.gltf(filepath=file_path)
                bpy.ops.wm.usd_export(filepath=join(cur_output_folder, f'{file_name}_.usd'),
                                      relative_paths=True)
                bpy.ops.wm.read_factory_settings(use_empty=True)
                bpy.ops.wm.usd_import(filepath=join(cur_output_folder, f'{file_name}_.usd'))
                for obj in bpy.data.objects:
                    if obj.name.endswith('_root'):
                        obj.name = f'_{file_name}'
                bpy.ops.wm.usd_export(filepath=join(cur_output_folder, f'{file_name}.usd'),
                                      relative_paths=True)
                os.remove(join(cur_output_folder, f'{file_name}_.usd'))
                
    
    def decompress_glb(self, input_path, output_path):
        import subprocess
        cmd = [
            "gltf-transform",
            "ktxdecompress",
            input_path,
            output_path
        ]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print('I am print decompress glb result')
            print(result)

        except subprocess.CalledProcessError as e:
            print('throw out exception')
            pass

    def transform_usd(self, info_path, source_folder, output_folder):
        import bpy
        from scipy.spatial.transform import Rotation as R
        from transforms3d.quaternions import mat2quat, quat2mat

        with open(info_path, 'r') as json_file:
            info = json.load(json_file)
        json_file.close()

        object_instance = info["object_instances"]
        
        for folder in os.listdir(source_folder):
            flag = False
            for item in object_instance:
                if item["template_name"] == folder:
                    usd_path = join(join(source_folder, folder), f'{folder}.usd')
                    if "translation" in item.keys():
                        translation = item["translation"]
                    else:
                        translation = [0, 0, 0]
                    if "rotation" in item.keys():
                        rotation = item["rotation"]
                    else:
                        rotation = [1, 0, 0, 0]
                    if "non_uniform_scale" in item.keys():
                        scale = item["non_uniform_scale"]
                    else:
                        scale = [1, 1, 1]
                    bpy.ops.wm.read_factory_settings(use_empty=True)
                    bpy.ops.wm.usd_import(filepath=usd_path)
                    # transform from habitat coordinate to isaac coordinate
                    x, y, z = translation
                    translation = [x, -z, y]
                    w, x, y, z = rotation
                    rotation = [x, y, z, w]
                    r = R.from_quat(rotation)
                    euler_rad = r.as_euler('xyz', degrees=False)
                    euler_x, euler_y, euler_z = euler_rad
                    euler_rad = [euler_x, -euler_z, euler_y]
                    x, y, z = scale
                    scale = [x, z, y]

                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    for obj in bpy.context.scene.objects:
                        if obj.type == 'MESH':
                            obj.rotation_mode = 'XZY'
                            obj.location = tuple(translation)
                            obj.rotation_euler = tuple(euler_rad)
                            obj.scale = tuple(scale)
                            
                    bpy.ops.wm.usd_export(filepath=join(join(output_folder, folder), f'{folder}.usd'))
                    flag = True
                    break

            if not flag:
                bpy.ops.wm.read_factory_settings(use_empty=True)
                bpy.ops.wm.usd_import(filepath=join(join(source_folder, folder), f'{folder}.usd'))
                bpy.ops.wm.usd_export(filepath=join(join(output_folder, folder), f'{folder}.usd'))

    def rename_textures_and_update_usd(self, usd_file_path):
        from pxr import Usd, UsdShade, Sdf

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
                            
    def modify_usds_texture(self, source_folder):
        # folder_path = './data/103997643_171030747_demo_usd/'

        for folder in os.listdir(source_folder):
            usd_path = join(join(source_folder, folder), f'{folder}.usd')
            self.rename_textures_and_update_usd(usd_path)

    def merge_all_usds(self, source_folder, output_path):
        # usd_file_path = './data/103997643_171030747_demo_usd_transfer'
        # output_usd_file = "./transfer_output/final.usd"

        import bpy

        bpy.ops.wm.read_factory_settings(use_empty=True)

        input_usd_files = []
        
        for folder in os.listdir(source_folder):
            input_usd_files.append(join(join(source_folder, folder), f'{folder}.usd'))

        # 将所有 USD 文件导入 Blender
        for usd_path in input_usd_files:
            if os.path.exists(usd_path):
                bpy.ops.wm.usd_import(filepath=usd_path)
            else:
                print(f"File not found: {usd_path}")

        # root = bpy.data.objects.new("root", None)
        # bpy.context.collection.objects.link(root)

        # for obj in bpy.data.objects:
        #     if obj != root and obj.parent is None:
        #         obj.parent = root

        # 选择所有对象以便导出
        # for obj in bpy.data.objects:
        #     obj.select_set(True)

        # 设置导出参数并导出合并后的 USD 文件
        bpy.ops.wm.usd_export(
            filepath=output_path,
            export_textures=True,            # 导出纹理（可选）
            export_materials=True,           # 导出材质
            selected_objects_only=False,     # 导出所有对象
            export_animation=True,           # 是否导出动画（视情况而定）
            root_prim_path="/root"
        )


class GLB2OBJ():
    def __init__(self):
        self.converter = Converter()
        pass
    
    def convert(self, source_path, output_folder, scene_config_file):
        scene_name = scene_config_file.split('/')[-1].split('.')[0]
        if not os.path.exists(join(output_folder, f'{scene_name}')):
            self.copy_scene(scene_config_file, source_path, join(output_folder, f'{scene_name}'))
        
        if os.path.exists(join(output_folder, f'{scene_name}_obj')):
            shutil.rmtree(join(output_folder, f'{scene_name}_obj'))
        os.makedirs(join(output_folder, f'{scene_name}_obj'))

        obj_path_list = ['objects/dynamic', 'objects/static', 'stages']
        for obj_path in obj_path_list:
            for file in os.listdir(join(join(output_folder, f'{scene_name}'), obj_path)):
                file_name = file.split('.')[0]
                file_path = join(join(join(output_folder, f'{scene_name}'), obj_path), file)
                self.convert_glb2obj(file_path, join(join(output_folder, f'{scene_name}_obj'), file_name), file_name)


    def copy_scene(self, scene_config_file, source_folder, output_folder):
        raw_stage_folder = join(source_folder, "stages")
        raw_object_folder = join(source_folder, "objects")

        with open(scene_config_file, 'r') as json_file:
            json_text = json.load(json_file)
        json_file.close()

        stage = json_text["stage_instance"]
        objects = json_text["object_instances"]

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        stage_folder = join(output_folder, 'stages')
        object_folder = join(output_folder, 'objects')
        static_folder = join(object_folder, 'static')
        dynamic_folder = join(object_folder, 'dynamic')

        os.makedirs(static_folder, exist_ok=True)
        os.makedirs(dynamic_folder, exist_ok=True)
        os.makedirs(stage_folder, exist_ok=True)

        stage_name = stage['template_name'].split('/')[-1]

        if os.path.exists(join(raw_stage_folder, stage_name + '.glb')):
            shutil.copy(join(raw_stage_folder, stage_name + '.glb'), stage_folder)
            self.converter.decompress_glb(join(stage_folder, stage_name + '.glb'), join(stage_folder, stage_name + '.glb'))

        for obj in objects:
            obj_name = obj['template_name']
            static = obj['motion_type']
            obj_path = None
            if static == 'STATIC':
                for dir in os.listdir(raw_object_folder):
                    if dir == 'decomposed':
                        continue
                    if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                        obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                        break
                if obj_path is not None:
                    shutil.copy(obj_path, static_folder)
                    obj_base = os.path.basename(obj_path)
                    self.converter.decompress_glb(join(static_folder, obj_base), join(static_folder, obj_base))
                else:
                    print(f'{obj_name} can not found')
                    pass
            else:
                for dir in os.listdir(raw_object_folder):
                    if dir == 'decomposed':
                        continue
                    if os.path.exists(join(join(raw_object_folder, dir), obj_name + '.glb')):
                        obj_path = join(join(raw_object_folder, dir), obj_name + '.glb')
                        break
                if obj_path is not None:
                    shutil.copy(obj_path, dynamic_folder)
                    obj_base = os.path.basename(obj_path)
                    self.converter.decompress_glb(join(dynamic_folder, obj_base), join(dynamic_folder, obj_base))
                else:
                    print(f'{obj_name} can not found')
                    pass

        shutil.copy(scene_config_file, output_folder)

    def convert_glb2obj(self, glb_path, output_folder, obj_name):
        import bpy
        import subprocess

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        else:
            print(f'{output_folder} already exists, I will recreate it.')
            shutil.rmtree(output_folder)
            os.makedirs(output_folder)

        obj_path = join(output_folder, obj_name + '.obj')

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

        subprocess.run([
            "gltf-transform", "palette",
            glb_path,
            join(output_folder, 'texture.json')
        ], check=True)

        with open(join(output_folder, 'texture.json'), 'r') as json_file:
            json_text = json.load(json_file)
        json_file.close()

        if "images" in json_text.keys():
            images = json_text["images"]
        else:
            images = None
        if "materials" in json_text.keys():
            materials = json_text["materials"]
        else:
            materials = None

        self.converter.material_decompose(join(output_folder, obj_name + '.mtl'), output_folder)
        self.converter.split_obj_by_material(join(output_folder, obj_name + '.obj'), output_folder)

        if not os.path.exists(join(output_folder, 'textures')):
            os.makedirs(join(output_folder, 'textures'))
        
        for material in materials:
            name = material['name']
            if 'pbrMetallicRoughness' in material.keys():
                pbrMetallicRoughness = material['pbrMetallicRoughness']
                if 'baseColorTexture' in pbrMetallicRoughness.keys():
                    baseColorTexture = pbrMetallicRoughness['baseColorTexture']
                    index = baseColorTexture['index']
                    image = images[index]
                    image_path = join(output_folder, image['uri'])
                    image_suffix = image['uri'].split('.')[-1]
                    new_image_path = join(output_folder, f'textures/{obj_name}_{name}.{image_suffix}')
                    shutil.copy2(image_path, new_image_path)

                    if not os.path.exists(join(output_folder, obj_name + '_' + name + '.mtl')):
                        continue
                    with open(join(output_folder, obj_name + '_' + name + '.mtl'), 'r') as file:
                        text = file.read()
                    file.close()

                    if text[-1] == '\n':
                        path = 'textures/' + os.path.basename(new_image_path)
                        text = text + f'map_Kd {path}'
                    else:
                        path = 'textures/' + os.path.basename(new_image_path)
                        text = text + f'\nmap_Kd {path}'

                    with open(join(output_folder, obj_name + '_' + name + '.mtl'), 'w') as file:
                        file.write(text)
                    file.close()
        if images is not None:
            for image in images:
                if os.path.exists(join(output_folder, image['uri'])):
                    os.remove(join(output_folder, image['uri']))
        
        if os.path.exists(join(output_folder, obj_name + '.obj')):
            os.remove(join(output_folder, obj_name + '.obj'))
        if os.path.exists(join(output_folder, obj_name + '.mtl')):
            os.remove(join(output_folder, obj_name + '.mtl'))
        if os.path.exists(join(output_folder, 'texture.bin')):
            os.remove(join(output_folder, 'texture.bin'))
        if os.path.exists(join(output_folder, 'texture.json')):
            os.remove(join(output_folder, 'texture.json'))
        if os.path.exists(join(output_folder, obj_name + '.json')):
            os.remove(join(output_folder, obj_name + '.json'))

        for file in os.listdir(output_folder):
            if file.endswith('.mtl'):
                self.converter.write_mtl_json(join(output_folder, file), output_folder, path_prefix=f'{obj_name}/textures', file_name=output_folder.split('/')[-1])
        
    def transform_obj_file(self, obj_path, transform):
        import bpy
        from scipy.spatial.transform import Rotation as R

        tran = transform['translation']
        rot = transform['rotation']
        scale = transform['scale']

        x, y, z = tran
        tran = [x, -z, y]
        w, x, y, z = rot
        rot = [x, y, z, w]
        r = R.from_quat(rot)
        euler_rad = r.as_euler('xyz', degrees=False)
        euler_x, euler_y, euler_z = euler_rad
        euler_rad = [euler_x, -euler_z, euler_y]
        x, y, z = scale
        scale = [x, z, y]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.obj_import(filepath=obj_path)
        obj = bpy.context.selected_objects[0]
        obj.location = tuple(tran)
        obj.rotation_euler = tuple(euler_rad)
        obj.scale = tuple(scale)

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.ops.wm.obj_export(
            filepath=obj_path
        )

    def transform_objs(self, obj_folder, scene_config_json):
        with open(scene_config_json, 'r') as json_file:
            scene_config = json.load(json_file)
        json_file.close()

        obj_instance = scene_config['object_instances']
        
        for folder in os.listdir(obj_folder):
            for item in obj_instance:
                if item['template_name'] == folder:
                    translation = item["translation"]
                    rotation = item["rotation"]
                    scale = item["non_uniform_scale"]
                    transform = {"translation": translation,
                                 "rotation": rotation,
                                 "scale": scale}
                    for file in os.listdir(join(obj_folder, folder)):
                        if file.endswith('.obj'):
                            self.transform_obj_file(join(join(obj_folder, folder), file), transform)

    def merge_all_obj_file(self, obj_folder, output_path):
        geo_template = '<geom name="OBJ" type="mesh" mesh="OBJ" material="OBJ_mtl"/>'
        mesh_template = '<mesh name="OBJ" file="FOLDER/OBJ.obj" />'

        obj_list = []
        geo_list = []
        for folder in os.listdir(obj_folder):
            folder_path = join(obj_folder, folder)
            for file in os.listdir(folder_path):
                if file.endswith('.obj'):
                    obj_name = file.split('.')[0]
                    if os.path.exists(join(folder_path, obj_name + '.json')):
                        with open(join(folder_path, obj_name + '.json'), 'r') as json_file:
                            text = json.load(json_file)
                        json_file.close()
                        text_key = next(iter(text))
                        text = text[text_key]
                    if text + '\n' + mesh_template.replace('OBJ', obj_name).replace('FOLDER', f'./{folder}') not in obj_list:
                        obj_list.append(text + '\n' + mesh_template.replace('OBJ', obj_name).replace('FOLDER', f'./{folder}'))
                    geo = geo_template.replace('OBJ', obj_name)
                    geo_list.append(geo)

        with open(output_path, 'w') as xml_file:
            xml_file.write('<mujoco model="minimal">\n\t<asset>\n')
            for obj in obj_list:
                xml_file.write(obj)
            xml_file.write('\t</asset>\n\t<worldbody>\n')
            for geo in geo_list:
                xml_file.write(geo)
            xml_file.write('\t</worldbody>\n</mujoco>')
        xml_file.close()

        self.converter.pretty_print_xml(output_path)
        



