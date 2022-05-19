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

pyrosim.Start_SDF("boxes.sdf")

cubes = []

# generate cubes
for x in range(5):
    for y in range(5):  
        l = 1
        w = 1
        h = 1
        zpos = 0.5
        for k in range(10):
            cubes.append(Box(dims=[l,w,h], pos=[x,y,zpos]))
            l *= 0.9
            w *= 0.9
            h *= 0.9
            zpos += 1

# Send cubes to sdf 
for cube in cubes:
    pyrosim.Send_Cube(name="Box", pos=cube.pos, size=cube.dims)

pyrosim.End()

