import os
import sys
sys.path.append(os.getcwd())

from convert import GLB2USD

glb2usd = GLB2USD()


source_path = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/'
output_folder = './data/103997643_171030747_demo'
scene_config_file = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json'

glb2usd.convert(source_path, output_folder, scene_config_file)

# source_path = '/home/diligent/Desktop/Git_local_foler/Assets/data/assets'
# output_folder = './data/metascene_fix'
# scene_config_file = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json'


# glb2usd.convert_wo_copy(source_path, output_folder, 'metascene_fix')