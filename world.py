import pybullet as p 

class World:
    def __init__(self, solutionId, dir='.'):
        self.planeId = p.loadURDF("plane.urdf")
        worldFile = f"{dir}/world_{solutionId}.sdf"
        try:
            self.objectId = p.loadSDF(worldFile)
        except:
            self.objectId = p.loadSDF(f"{dir}/world.sdf")

