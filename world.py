import os
import pybullet as p 

class World:
    def __init__(self, solutionId):
        self.planeId = p.loadURDF("plane.urdf")
        worldFile = "world_" + str(solutionId) + ".sdf"
        if os.path.exists(worldFile):
            p.loadSDF(worldFile)
        else:
            p.loadSDF("world.sdf")
