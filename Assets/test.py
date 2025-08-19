# import bpy
# import subprocess
# import os
# from os.path import join
# import json
# from convert import Converter, GLB2OBJ
# import shutil

# my_converter = Converter()
# glb2obj = GLB2OBJ()


# glb_path = './assets/objects/static/0b0e6df6479ffd5c48f58de1330e7f2ab1248620.glb'
# output_folder = './test_obj'
# obj_name = '0b0e6df6479ffd5c48f58de1330e7f2ab1248620'


# glb2obj.convert_glb2obj(glb_path, join(output_folder, obj_name), obj_name)

import numpy as np
from scipy.spatial.transform import Rotation as R

pos = np.array([-2.4721601009368896, 2.3815989891318168e-07, -3.9956598284447153])
quat = np.array([1.0, -4.939599724517467e-11, 0.0, 0.0])

x, y, z = pos
translation = [x, -z, y]
w, x, y, z = quat
rotation = [x, y, z, w]
r = R.from_quat(rotation)
euler_rad = r.as_euler('xyz', degrees=False)
euler_x, euler_y, euler_z = euler_rad
euler_rad = [euler_x, -euler_z, euler_y]

from IPython import embed; embed()