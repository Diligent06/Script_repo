import mujoco
from mujoco import mjcf

# Path to your URDF file
urdf_path = "7221/7221.urdf"

# Load the URDF as an MJCF object
mjcf_model = mjcf.from_urdf(urdf_path)

# Save the MJCF to a file
mjcf_model.to_xml_file("7221.xml")
