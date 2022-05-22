import pyrosim.pyrosim as pyrosim

# generate.py
# this file will: 
#    1. specify links for simulation in pybullet
#    2. generate a .sdf file that simulate.py will read and use in pybullet

class Box:
    def __init__(self, dims, pos):
        # dimensions are [l,w,h]
        self.dims = dims
        # location is [x,y,z]
        self.pos = pos

def Get_Cubes():
    cubes = []
    # generate cubes
    l = 1
    w = 1
    h = 1
    x = -4
    y = 4
    z = 0.5
    cubes.append(Box(dims=[l,w,h], pos=[x,y,z]))

    return cubes

def Create_Robot(start_x, start_y, start_z):
    pyrosim.Start_URDF("body.urdf")

    # the first link and the first joint have absolute positions
    pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])
    pyrosim.Send_Joint(name="Torso_BackLeg", parent="Torso", child="BackLeg", type="revolute", position=[start_x-0.5, start_y,start_z-0.5])
    # now all links & joints with an upstream joint have positions relative to the upstream joint
    pyrosim.Send_Joint(name="Torso_FrontLeg", parent="Torso", child="FrontLeg", type="revolute", position=[start_x+0.5, start_y,start_z-0.5])
    pyrosim.Send_Cube(name="FrontLeg", pos=[0.5,0,-0.5], size=[1,1,1])
    pyrosim.Send_Cube(name="BackLeg", pos=[-0.5,0,-0.5], size=[1,1,1])
    

    pyrosim.End()
    
def Create_World():
    pyrosim.Start_SDF("world.sdf")

    cubes = Get_Cubes()

    # Send cubes to sdf 
    for cube in cubes:
        pyrosim.Send_Cube(name="Box", pos=cube.pos, size=cube.dims)

    pyrosim.End()

Create_World()
Create_Robot(0,0,1.5)

