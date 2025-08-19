import trimesh
import argparse
import os
from os.path import join
import json
import shutil
import numpy as np
import habitat_sim
import pymeshlab

def asset_decimation(asset_raw, asset_deci=None, deci_point_num=40000):
    mesh_raw = trimesh.load(asset_raw, force='mesh')
    mesh_raw.export("./temp.obj")
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh("./temp.obj")
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(deci_point_num))
    ms.save_current_mesh('./temp.obj')
    simplified_mesh = trimesh.load('./temp.obj')
    if asset_deci is not None:
        simplified_mesh.export(asset_deci)
    else:
        simplified_mesh.export(asset_raw)

def cal_navmesh(scene, scene_dataset, navmesh_save_path):
    rgb_sensor = True
    depth_sensor = True
    semantic_sensor = True
    sim_settings = {
        "width": 256,
        "height": 256,
        "scene": scene,
        "scene_dataset": scene_dataset,
        "default_agent": 0,
        "sensor_height": 1.5,
        "color_sensor": rgb_sensor,
        "depth_sensor": depth_sensor,
        "semantic_sensor": semantic_sensor,
        "seed": 1,
        "enable_physics": False
    }
    cfg = make_cfg(sim_settings)
    sim = habitat_sim.Simulator(cfg)
    sim.navmesh_visualization = True

    navmesh_settings = habitat_sim.NavMeshSettings()
    navmesh_settings.set_defaults()
    
    # fmt: off
    #@markdown ---
    #@markdown ## Configure custom settings (if use_custom_settings):
    #@markdown Configure the following NavMeshSettings for customized NavMesh recomputation.
    #@markdown **Voxelization parameters**:
    navmesh_settings.cell_size = 0.02 #@param {type:"slider", min:0.01, max:0.2, step:0.01}
    #default = 0.05
    navmesh_settings.cell_height = 0.05 #@param {type:"slider", min:0.01, max:0.4, step:0.01}
    #default = 0.2

    #@markdown **Agent parameters**:
    navmesh_settings.agent_height = 1.5 #@param {type:"slider", min:0.01, max:3.0, step:0.01}
    #default = 1.5
    navmesh_settings.agent_radius = 0.1 #@param {type:"slider", min:0.01, max:0.5, step:0.01}
    #default = 0.1
    navmesh_settings.agent_max_climb = 0.2 #@param {type:"slider", min:0.01, max:0.5, step:0.01}
    #default = 0.2
    navmesh_settings.agent_max_slope = 45 #@param {type:"slider", min:0, max:85, step:1.0}
    # default = 45.0
    # fmt: on
    # @markdown **Navigable area filtering options**:
    navmesh_settings.filter_low_hanging_obstacles = True  # @param {type:"boolean"}
    # default = True
    navmesh_settings.filter_ledge_spans = True  # @param {type:"boolean"}
    # default = True
    navmesh_settings.filter_walkable_low_height_spans = True  # @param {type:"boolean"}
    # default = True

    # fmt: off
    #@markdown **Detail mesh generation parameters**:
    #@markdown For more details on the effects
    navmesh_settings.region_min_size = 20 #@param {type:"slider", min:0, max:50, step:1}
    #default = 20
    navmesh_settings.region_merge_size = 20 #@param {type:"slider", min:0, max:50, step:1}
    #default = 20
    navmesh_settings.edge_max_len = 12.0 #@param {type:"slider", min:0, max:50, step:1}
    #default = 12.0
    navmesh_settings.edge_max_error = 1.3 #@param {type:"slider", min:0, max:5, step:0.1}
    #default = 1.3
    navmesh_settings.verts_per_poly = 6.0 #@param {type:"slider", min:3, max:6, step:1}
    #default = 6.0
    navmesh_settings.detail_sample_dist = 6.0 #@param {type:"slider", min:0, max:10.0, step:0.1}
    #default = 6.0
    navmesh_settings.detail_sample_max_error = 1.0 #@param {type:"slider", min:0, max:10.0, step:0.1}
    # default = 1.0
    # fmt: on

    # @markdown **Include STATIC Objects**:
    # @markdown Optionally include all instanced RigidObjects with STATIC MotionType as NavMesh constraints.
    navmesh_settings.include_static_objects = True  # @param {type:"boolean"}
    # default = False

    navmesh_success = sim.recompute_navmesh(sim.pathfinder, navmesh_settings)
    if navmesh_success:
        sim.pathfinder.save_nav_mesh(navmesh_save_path)
        print('Saved NavMesh to "' + navmesh_save_path + '"')
    else:
        print('Failed NavMesh generation!')
    return

def make_cfg(settings):
    sim_cfg = habitat_sim.SimulatorConfiguration()
    sim_cfg.gpu_device_id = 0
    sim_cfg.scene_id = settings["scene"]
    sim_cfg.scene_dataset_config_file = settings["scene_dataset"]
    sim_cfg.enable_physics = settings["enable_physics"]

    # Note: all sensors must have the same resolution
    sensor_specs = []

    color_sensor_spec = habitat_sim.CameraSensorSpec()
    color_sensor_spec.uuid = "color_sensor"
    color_sensor_spec.sensor_type = habitat_sim.SensorType.COLOR
    color_sensor_spec.resolution = [settings["height"], settings["width"]]
    color_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
    color_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(color_sensor_spec)

    depth_sensor_spec = habitat_sim.CameraSensorSpec()
    depth_sensor_spec.uuid = "depth_sensor"
    depth_sensor_spec.sensor_type = habitat_sim.SensorType.DEPTH
    depth_sensor_spec.resolution = [settings["height"], settings["width"]]
    depth_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
    depth_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(depth_sensor_spec)

    semantic_sensor_spec = habitat_sim.CameraSensorSpec()
    semantic_sensor_spec.uuid = "semantic_sensor"
    semantic_sensor_spec.sensor_type = habitat_sim.SensorType.SEMANTIC
    semantic_sensor_spec.resolution = [settings["height"], settings["width"]]
    semantic_sensor_spec.position = [0.0, settings["sensor_height"], 0.0]
    semantic_sensor_spec.sensor_subtype = habitat_sim.SensorSubType.PINHOLE
    sensor_specs.append(semantic_sensor_spec)

    # Here you can specify the amount of displacement in a forward action and the turn angle
    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = sensor_specs
    agent_cfg.action_space = {
        "move_forward": habitat_sim.agent.ActionSpec(
            "move_forward", habitat_sim.agent.ActuationSpec(amount=0.25)
        ),
        "turn_left": habitat_sim.agent.ActionSpec(
            "turn_left", habitat_sim.agent.ActuationSpec(amount=30.0)
        ),
        "turn_right": habitat_sim.agent.ActionSpec(
            "turn_right", habitat_sim.agent.ActuationSpec(amount=30.0)
        ),
    }

    return habitat_sim.Configuration(sim_cfg, [agent_cfg])

class PathError(Exception):
    pass
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    try:
        project_path = os.getenv("PROJ_PATH")
        if project_path is None:
            raise EnvironmentError('PROJ_PATH environment variable has not been set.')
        parser.add_argument(
            "--glb_folder_path",
            default=join(project_path, "data/assets/"),
            type=str
        )
        parser.add_argument(
            "--output_folder",
            default=join(project_path, "data/"),
            type=str
        )
        parser.add_argument(
            "--dataset_name",
            default="Habitat_data",
            type=str,
            help='Name of dataset'
        )
        parser.add_argument(
            "--scene_name",
            default="apt_0",
            type=str,
            help='Name of scene instance'
        )
        parser.add_argument(
            "--use_urdf",
            default=False,
            type=bool,
            help='Whether need to convert urdf files'
        )
        parser.add_argument(
            '--scale',
            default=1.0,
            type=float,
            help='object scale in scene'
        )
        args = parser.parse_args()

        if not os.path.exists(args.glb_folder_path):
            raise PathError('args.glb_folder_path not exist!')
        configs_static_objects_path = join(join(args.output_folder, args.dataset_name), "configs/objects/static/")
        configs_dynamic_objects_path = join(join(args.output_folder, args.dataset_name), "configs/objects/dynamic/")
        configs_stages_path = join(join(args.output_folder, args.dataset_name), "configs/stages/")
        static_objects_path = join(join(args.output_folder, args.dataset_name), "objects/static/")
        static_objects_save_path = "../../../objects/static/"
        dynamic_objects_path = join(join(args.output_folder, args.dataset_name), "objects/dynamic/")
        dynamic_objects_save_path = "../../../objects/dynamic/"
        stages_path = join(join(args.output_folder, args.dataset_name), "stages/")
        stages_save_path = "../../stages/"
        configs_scenes_path = join(join(args.output_folder, args.dataset_name), 'configs/scenes/')
        configs_lighting_path = join(join(args.output_folder, args.dataset_name), 'configs/lighting/')
        configs_ssd_path = join(join(args.output_folder, args.dataset_name), 'configs/ssd/')
        configs_navmeshes_path = join(join(args.output_folder, args.dataset_name), 'navmeshes/')
        urdf_path = join(join(args.output_folder, args.dataset_name), "urdfs/")
        urdf_save_path = '../../urdfs'
        os.makedirs(configs_static_objects_path, exist_ok=True)
        os.makedirs(configs_dynamic_objects_path, exist_ok=True)
        os.makedirs(configs_stages_path, exist_ok=True)
        os.makedirs(static_objects_path, exist_ok=True)
        os.makedirs(dynamic_objects_path, exist_ok=True)
        os.makedirs(stages_path, exist_ok=True)
        os.makedirs(configs_scenes_path, exist_ok=True)
        os.makedirs(configs_lighting_path, exist_ok=True) 
        os.makedirs(configs_ssd_path, exist_ok=True)
        os.makedirs(configs_navmeshes_path, exist_ok=True)
        os.makedirs(urdf_path, exist_ok=True)
        
        scene_data = {}
        object_instance = []
        stage_instance = {}
        max_height = 0
        semantic_id = []

        # add static objects to new scene
        for _id, file_name in enumerate(os.listdir(join(args.glb_folder_path, "objects/static"))):
            # copy .glb file to new folder
            source_file_path = os.path.join(join(args.glb_folder_path, "objects/static/"), file_name)
            destination_file_path = os.path.join(static_objects_path, file_name)
            # print(destination_file_path)
            shutil.copyfile(source_file_path, destination_file_path)
            # generate .object_config.json file for each object
            prefix = os.path.splitext(file_name)[0]
            json_file_path = join(configs_static_objects_path, (prefix + ".object_config.json"))
            data = {
                "render_asset": static_objects_save_path + file_name,
                "collision_asset": static_objects_save_path + file_name
            }
            semantic_id.append({"name": prefix, "id": _id + 1})
            # generate object instance dictionary
            mesh = trimesh.load(static_objects_path + file_name)
            instance = {}
            instance.update({"template_name": "objects/static/"+prefix, "motion_type": "STATIC", \
                             "translation": mesh.centroid.tolist(),\
                             "transformation": {"scale": [args.scale, args.scale, args.scale]}})
            object_instance.append(instance)
            max_height = np.maximum(max_height, mesh.centroid[1])
            # dump json data of each object
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            json_file.close()

        # add dynamic objects to new scene
        for _id, file_name in enumerate(os.listdir(join(args.glb_folder_path, "objects/dynamic"))):
            # copy .glb file to new folder
            source_file_path = os.path.join(join(args.glb_folder_path, "objects/dynamic/"), file_name)
            destination_file_path = os.path.join(dynamic_objects_path, file_name)
            shutil.copyfile(source_file_path, destination_file_path)
            # Large dynamic object decimation
            if os.path.getsize(destination_file_path) / 1048576 > 10: # convert to Mb
                asset_decimation(destination_file_path)
                print(f"Decimation: {destination_file_path}")
            # generate .object_config.json file for each object
            prefix = os.path.splitext(file_name)[0]
            json_file_path = join(configs_dynamic_objects_path, (prefix + ".object_config.json"))
            data = {
                "render_asset": dynamic_objects_save_path + file_name,
                "collision_asset": dynamic_objects_save_path + file_name
            }
            semantic_id.append({"name": prefix, "id": _id + 1})
            # generate object instance dictionary
            mesh = trimesh.load(dynamic_objects_path + file_name)
            instance = {}
            instance.update({"template_name": "objects/dynamic/"+prefix,
                            "motion_type": "DYNAMIC",
                            'margin': 0.04,
                            "mass": 50,
                            "linear_damping": 1,
                            "angular_damping": 1,
                            "friction_coefficient": 1,
                            "restitution_coefficient": 0.01,
                            "translation": mesh.centroid.tolist(),\
                            "transformation": {"scale": [args.scale, args.scale, args.scale]}})
            object_instance.append(instance)
            max_height = np.maximum(max_height, mesh.centroid[1])
            # dump json data of each object
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            json_file.close()

        # add base stage for new scene
        for file_name in os.listdir(args.glb_folder_path + "stages"):
            # copy .glb file to new folder
            source_file_path = os.path.join(join(args.glb_folder_path, "stages/"), file_name)
            destination_file_path = os.path.join(stages_path, file_name)
            shutil.copyfile(source_file_path, destination_file_path)
            # generate .object_config.json file for each object
            prefix = os.path.splitext(file_name)[0]
            json_file_path = join(configs_stages_path, (prefix + ".stage_config.json"))
            data = {
                "render_asset": stages_save_path + file_name,
                "collision_asset": stages_save_path + file_name
            }
            # update first stage instance to scene
            if "template_name" not in stage_instance:
                mesh = trimesh.load(args.glb_folder_path + 'stages/' + file_name)
                bounds = mesh.bounds
                stage_instance.update({"template_name": "stages/" + prefix, \
                                       "translation": mesh.centroid.tolist(),\
                                       "transformation": {"scale": [args.scale, args.scale, args.scale]}})
                scene_prefix = prefix
            # dump json data of each stage
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            json_file.close()
        
        # add articulated object to new scene
        if args.use_urdf:
            articulated_instance = []
            for f in os.scandir(join(args.glb_folder_path, 'urdfs/')):
                dest_path = os.path.join(urdf_path, os.path.basename(f.path))
                shutil.copytree(f.path, dest_path, dirs_exist_ok=True)
                if os.path.exists(join(join(urdf_path, os.path.basename(f.path)), f'{os.path.basename(f.path)}.urdf')):
                    name = os.path.basename(f.path)
                    articulated_dict = {}
                    articulated_dict.update({"template_name": name, "translation_origin": "COM", "fixed_base": True, "uniform_scale": 1, "motion_type": "DYNAMIC"})
                    articulated_instance.append(articulated_dict)
                # for file in os.listdir(os.path.join(urdf_path, os.path.basename(f.path))):
                #     if file.endswith('.urdf'):
                #         name, ext = os.path.splitext(file)
                #         articulated_dict = {}
                #         articulated_dict.update({"template_name": name, "translation_origin": "COM", "fixed_base": True, "uniform_scale": 1, "motion_type": "DYNAMIC"})
                #         articulated_instance.append(articulated_dict)

        # add default lighting in the scene
        scene_data.update({"default_lighting": "lighting/" + scene_prefix})

        # integrate scene data and dump it to json file
        scene_data.update({"stage_instance": stage_instance, "object_instances": object_instance})
        if args.use_urdf:
            scene_data.update({"articulated_object_instances": articulated_instance})

        with open(configs_scenes_path + args.scene_name + '.scene_instance.json', 'w') as scene_json:
            json.dump(scene_data, scene_json, indent=4)
        scene_json.close()

        # generate light data of the scene
        light_x = np.arange(bounds[0, 0], bounds[1, 0], 1)
        light_y = np.arange(bounds[0, 2], bounds[1, 2], 1)
        assert len(light_x) != 0 or len(light_y) != 0
        
        light_grid = np.meshgrid(light_x, light_y)
        grid_x = light_grid[0].flatten()
        grid_y = light_grid[1].flatten()
        lighting_instance = {}
        for i in range(len(grid_x)):
            light = {}
            light.update({"type": "point", "position": [grid_x[i], 2, grid_y[i]], \
                            "intensity": 1.1, "color": [0.93, 0.98, 1]})
            lighting_instance.update({str(i): light})
        with open(join(configs_lighting_path, (scene_prefix + '.lighting_config.json')), 'w') as light_json:
            json.dump(lighting_instance, light_json, indent=4)
        light_json.close()

        # generate semantic id
        with open(join(configs_ssd_path, (args.scene_name + '_semantic_lexicon.json')), 'w') as semantic_json:
            json.dump({"classes": semantic_id}, semantic_json, indent=4)
        semantic_json.close()

        # generate scene_dataset config json file
        stage_dict = {"paths": {".json": ['configs/stages']}}
        object_dict = {"paths": {".json": ['configs/objects/static', 'configs/objects/dynamic']}}
        light_dict = {"default_attributes": {"positive_intensity_scale": 2.5, "negative_intensity_scale": 0.1}, \
                        "paths": {".json": ['configs/lighting']}}
        semantic_instance_dict = {"default_attributes": {"semantic_scene_instance": args.scene_name + '_ssd_map'}, \
                            "paths": {".json": ['configs/scenes']}}
        semantic_descriptor_dict = {args.scene_name + '_ssd_map': "configs/ssd/" + args.scene_name + "_semantic_lexicon.json"}
        with open(args.output_folder + args.dataset_name + '/' + scene_prefix + ".scene_dataset_config.json", 'w') as dataset_json:
            json.dump({"stages": stage_dict, \
                        "objects": object_dict, \
                        "articulated_objects": {"paths": {".urdf": ["urdfs/*/"]}}, \
                        "light_setups": light_dict, \
                        "scene_instances": semantic_instance_dict, \
                        "semantic_scene_descriptor_instances": semantic_descriptor_dict}, dataset_json, indent=4)
        dataset_json.close()
        
        # generate navmesh file for new scene
        cal_navmesh(join(configs_scenes_path, (args.scene_name + '.scene_instance.json')), \
                    join(join(args.output_folder, args.dataset_name), (scene_prefix + '.scene_dataset_config.json')), \
                    join(configs_navmeshes_path, (args.scene_name + '.navmesh')))
    except EnvironmentError as e:
        print(f"Environment Error occurred: {e}")
    except PathError as e:
        print(f"Path Error: {e}")
    
