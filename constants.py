import numpy as np

TIMESTEPS=1000
MAX_FORCE=50 # Newton*meters
GRAVITY_FORCE=-9.8 # m/s^2

# front and back leg constants
AMPLITUDE_BACK=np.pi/4.0
FREQUENCY_BACK=10
PHASE_OFFSET_BACK=np.pi/4.0

AMPLITUDE_FRONT=np.pi/4.0
FREQUENCY_FRONT=10
PHASE_OFFSET_FRONT=0.0

# evolutionary parameters
NUMBER_OF_GENERATIONS=100
