"""Sensor class for the Pyrosim environment."""
import pyrosim.pyrosim as pyrosim
import numpy as np

class Sensor:
    """Sensor class for the Pyrosim environment."""
    def __init__(self, name, timesteps):
        self.name = name
        self.timesteps = timesteps
        self.Prepare_To_Sense()

    def Get_Value(self, i):
        """Get the value of the sensor at time step i."""
        self.values[i] = pyrosim.Get_Touch_Sensor_Value_For_Link(self.name)
        return self.values[i]

    def Prepare_To_Sense(self):
        """Prepare the sensor to sense."""
        self.values = np.zeros(self.timesteps)
