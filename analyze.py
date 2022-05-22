import numpy as np
import matplotlib.pyplot

targetAngles_front = np.load("data/targetAngles_front.npy")
targetAngles_back = np.load("data/targetAngles_back.npy")
matplotlib.pyplot.plot(targetAngles_front, label="front leg target angles")
matplotlib.pyplot.plot(targetAngles_back, label="back leg target angles")
matplotlib.pyplot.legend()
matplotlib.pyplot.show()
exit()

backLegSensorValues = np.load("data/backLegSensor.npy")
frontLegSensorValues = np.load("data/frontLegSensor.npy")

matplotlib.pyplot.plot(backLegSensorValues, label="backLeg")
matplotlib.pyplot.plot(frontLegSensorValues, label="frontLeg")

matplotlib.pyplot.legend()

matplotlib.pyplot.show()

