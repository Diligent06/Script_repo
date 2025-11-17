import os
import sys
sys.path.append(os.getcwd())

from convert import GLB2USD

glb2usd = GLB2USD()


source_path = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/'
output_folder = './data/all_scenes'
scene_config_prefix = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered'
for file in os.listdir(scene_config_prefix):
    if file.endswith('.scene_instance.json'):
        scene_config_file = os.path.join(scene_config_prefix, file)
        print(f'Converting {scene_config_file}...')
        glb2usd.convert(source_path, output_folder, scene_config_file)
# scene_config_file = '/108736689_177263340.scene_instance.json'

# glb2usd.convert(source_path, output_folder, scene_config_file)

# source_path = '/home/diligent/Desktop/Git_local_foler/Assets/data/assets'
# output_folder = './data/metascene_fix'
# scene_config_file = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json'


# glb2usd.convert_wo_copy(source_path, output_folder, 'metascene_fix')