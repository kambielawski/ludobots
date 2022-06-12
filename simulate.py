import pyrosim.pyrosim as pyrosim
import pybullet as p
import pybullet_data
import time
import numpy as np
import random
import sys

from robot import Robot
from world import World
from simulation import Simulation
import constants as c

# runMode can be GUI or DIRECT
if len(sys.argv) > 2:
    runMode = sys.argv[1]
    solnId = int(sys.argv[2])
    if len(sys.argv) > 3:
        brainFile = sys.argv[3]
    else:
        brainFile = None
else:
    runMode = "DIRECT"
    solnId = 0

simulation = Simulation(runMode, solnId)
world = World(solnId)
robots = [Robot(solnId, "body_0.urdf", brainFile)]


simulation.Run(robots)
simulation.Get_Fitness()



