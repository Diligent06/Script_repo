from omni.isaac.kit import SimulationApp

# Launch Isaac Sim
simulation_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

# Get stage interface
from pxr import Usd, UsdGeom
import omni.usd

# Get the stage
stage = omni.usd.get_context().get_stage()

# Load USD file
# usd_path = "./data/102343992_final/102343992.usd"
usd_path = './data/103997643_171030747_demo/103997643_171030747_demo_final/103997643_171030747_demo.usd'
omni.usd.get_context().open_stage(usd_path)

# Run simulation
while simulation_app.is_running():
    simulation_app.update()

simulation_app.close()