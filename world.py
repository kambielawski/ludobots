import os
import pybullet as p 

class World:
    def __init__(self, solutionId, dir='.'):
        self.planeId = p.loadURDF("plane.urdf")
        worldFile = f"{dir}/world_{solutionId}.sdf"
        try:
            p.loadSDF(worldFile)
        except:
            p.loadSDF(f"{dir}/world.sdf")

# if os.path.exists(worldFile):
#     p.loadSDF(worldFile)
# else:
#     p.loadSDF(f"{dir}/world.sdf")
