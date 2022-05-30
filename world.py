import pybullet as p 

class World:
    def __init__(self):
        self.planeId = p.loadURDF("plane.urdf")
        p.loadSDF("world.sdf")
