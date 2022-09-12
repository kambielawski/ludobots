import pyrosim.pyrosim as pyrosim
import pybullet as p
import numpy as np
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
windowSize = c.DEFAULT_EMPOWERMENT_WINDOW_SIZE

# runMode can be GUI or DIRECT
if argc > 1:
    runMode = sys.argv[1]
    if argc > 2:
        solnId = int(sys.argv[2])
        if argc > 3:
            brainFile = sys.argv[3]
            if argc > 4:
                bodyFile = sys.argv[4]
                if argc > 5:
                    windowSize = int(sys.argv[5])

simulation = Simulation(runMode, solnId)
world = World(solnId)
robots = [Robot(solnId, bodyFile, brainFile, windowSize)]


simulation.Run(robots)
simulation.Get_Fitness()



