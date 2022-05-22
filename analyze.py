import numpy as np
import matplotlib.pyplot

backLegSensorValues = np.load("data/backLegSensor.npy")
frontLegSensorValues = np.load("data/frontLegSensor.npy")

matplotlib.pyplot.plot(backLegSensorValues, label="backLeg")
matplotlib.pyplot.plot(frontLegSensorValues, label="frontLeg")

matplotlib.pyplot.legend()

matplotlib.pyplot.show()

