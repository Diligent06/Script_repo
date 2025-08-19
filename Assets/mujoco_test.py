import mujoco
mujoco.MjModel.from_xml_string('<mujoco/>')

import mujoco
from mujoco import MjModel, MjData
from mujoco.viewer import launch_passive

# model = mujoco.MjModel.from_xml_path("data/103997643_171030747_demo_mujoco/103997643_171030747_demo_obj_/scene.xml")
model = mujoco.MjModel.from_xml_path("/home/diligent/Desktop/isaac_ws/RoboVerse/assets/7221_mujoco/7221.xml")
data = mujoco.MjData(model)

# Launch interactive viewer
launch_passive(model, data)

input('press enter to exit ...')