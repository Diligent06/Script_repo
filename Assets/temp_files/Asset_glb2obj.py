from convert import GLB2OBJ
from os.path import join

glb2obj = GLB2OBJ()

source_path = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/'
output_folder = './data/103997643_171030747_demo_mujoco'
scene_config_file = '/home/diligent/Desktop/datasets/habitat_data/scenes/hssd-hab-home-robot/scenes-uncluttered/103997643_171030747_demo.scene_instance.json'

# glb2obj.convert(source_path, output_folder, scene_config_file)

glb2obj.transform_objs(join(output_folder, "103997643_171030747_demo_obj_"), scene_config_file)
glb2obj.merge_all_obj_file(join(output_folder, "103997643_171030747_demo_obj_"), 
                           join(join(output_folder, "103997643_171030747_demo_obj_"), 'scene.xml'))