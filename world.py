import pybullet as p 

class World:
    def __init__(self, solutionId):
        self.planeId = p.loadURDF("plane.urdf")
        p.loadSDF("world_" + str(solutionId) + ".sdf")
