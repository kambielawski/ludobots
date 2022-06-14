import sys
import numpy as np
import matplotlib.pyplot

'''
targetAngles_front = np.load("data/targetAngles_front.npy")

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
'''

expDataFile = sys.argv[1]

print(expDataFile)

expValues = np.load(expDataFile)
expValues_x = [pair[0] for pair in expValues]
expValues_y = [pair[1] for pair in expValues]

print(expValues)

matplotlib.pyplot.plot(expValues_x, expValues_y)
matplotlib.pyplot.ylim(1, max(expValues_y)+1)

matplotlib.pyplot.legend()

matplotlib.pyplot.show()

