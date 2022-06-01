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

def Generate_Body(start_x, start_y, start_z):
    # .urdf files are broadly used in the robotics community
    # "Universal Robot Description File"
    pyrosim.Start_URDF("body.urdf")

    # the first link and the first joint have absolute positions
    pyrosim.Send_Cube(name="Torso", pos=[start_x, start_y, start_z], size=[1,1,1])
    pyrosim.Send_Joint(name="Torso_BackLeg", parent="Torso", child="BackLeg", type="revolute", position=[start_x-0.5, start_y,start_z-0.5])
    # now all links & joints with an upstream joint have positions relative to the upstream joint
    pyrosim.Send_Joint(name="Torso_FrontLeg", parent="Torso", child="FrontLeg", type="revolute", position=[start_x+0.5, start_y,start_z-0.5])
    pyrosim.Send_Cube(name="FrontLeg", pos=[0.5,0,-0.5], size=[1,1,1])
    pyrosim.Send_Cube(name="BackLeg", pos=[-0.5,0,-0.5], size=[1,1,1])

    pyrosim.End()

def Generate_Brain():
    # .nndf files are just used in Pyrosim
    # "Neural Network Description File"
    pyrosim.Start_NeuralNetwork("brain.nndf")

    pyrosim.Send_Sensor_Neuron(name=0, linkName="Torso")
    pyrosim.Send_Sensor_Neuron(name=1, linkName="BackLeg")
    pyrosim.Send_Sensor_Neuron(name=2, linkName="FrontLeg")

    pyrosim.Send_Motor_Neuron(name=3, jointName="Torso_BackLeg")
    pyrosim.Send_Motor_Neuron(name=4, jointName="Torso_FrontLeg")

    pyrosim.End()

def Create_World():
    pyrosim.Start_SDF("world.sdf")

    cubes = Get_Cubes()

    # Send cubes to sdf 
    for cube in cubes:
        pyrosim.Send_Cube(name="Box", pos=cube.pos, size=cube.dims)

    pyrosim.End()

Create_World()
Generate_Body(0,0,1.5)
Generate_Brain()

