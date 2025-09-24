from convert import GLB2USD
import os
from os.path import join
import shutil

# folder_path = './data/103997643_171030747_demo/103997643_171030747_demo_add'
# name_list = ['stages', 'objects/dynamic', 'objects/static']
# for name in name_list:
#     cur_path = join(folder_path, name)
#     for file in os.listdir(cur_path):
#         if file.endswith('.glb'): 
#             os.rename(join(cur_path, file), join(cur_path, f'b{file}'))

glb2usd_convert = GLB2USD()

glb2usd_convert.convert_wo_copy(
    './data/103997643_171030747_demo/103997643_171030747_demo_add/objects/static/b0.glb',
    './data/103997643_171030747_demo/103997643_171030747_demo_add/objects/static',
    '0'
)

# glb2usd_convert.convert_glbs_usds('./data/103997643_171030747_demo/103997643_171030747_demo', 
#                                   './data/103997643_171030747_demo/103997643_171030747_demo_test_usd')

# glb2usd_convert.transform_usd(info_path, join(output_folder, f'{scene_name}_usd'), join(output_folder, f'{scene_name}_usd_transfer'))
# glb2usd_convert.modify_usds_texture(join(output_folder, f'{scene_name}_usd_transfer'))
# glb2usd_convert.merge_all_usds(join(output_folder, f'{scene_name}_usd_transfer'), join(join(output_folder, f'{scene_name}_final'), f'{scene_name}.usd'))

# import bpy

# bpy.ops.wm.read_factory_settings(use_empty=True)
# bpy.ops.wm.usd_import(filepath="data/103997643_171030747_demo/103997643_171030747_demo_test_usd/bb_cb00ebb224822113239b0ad246940f7f208570b3/bb_cb00ebb224822113239b0ad246940f7f208570b3.usd")
# file_name = 'bb_cb00ebb224822113239b0ad246940f7f208570b3'
# before_collections = set(bpy.data.collections.keys())
# for obj in bpy.data.objects:
#     if obj.name.endswith("______root"):
#         obj.name = file_name
# from IPython import embed; embed()
# # from IPython import embed; embed()
# bpy.ops.wm.usd_export(filepath="data/test.usd")