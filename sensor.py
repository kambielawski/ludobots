import pyrosim.pyrosim as pyrosim
import constants as c
import numpy as np

class Sensor:
    def __init__(self, name):
        self.name = name
        self.Prepare_To_Sense()

    def Get_Value(self, i):
        self.values[i] = pyrosim.Get_Touch_Sensor_Value_For_Link(self.name)

    def Prepare_To_Sense(self):
        self.values = np.zeros(c.TIMESTEPS)
