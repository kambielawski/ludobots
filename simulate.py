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

argc = len(sys.argv)

# default values
bodyFile = None
brainFile = None
runMode = "DIRECT"
solnId = 0

# runMode can be GUI or DIRECT
if argc > 1:
    runMode = sys.argv[1]
    if argc > 2:
        solnId = int(sys.argv[2])
        if argc > 3:
            brainFile = sys.argv[3]
            if argc > 4:
                bodyFile = sys.argv[4] 

simulation = Simulation(runMode, solnId)
world = World(solnId)
robots = [Robot(solnId, bodyFile, brainFile)]


simulation.Run(robots)
simulation.Get_Fitness()



