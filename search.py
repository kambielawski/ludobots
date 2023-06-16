from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
        'name': 'boxdisplacement-emp',
        'morphology': 'hexapod',
        'task_environment': './task_environments/box_world.sdf',
        'generations': 100,
        'target_population_size': 20,
        'motor_measure': 'VELOCITY', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['empowerment'], 
        'empowerment_window_size': 500,
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

afpo.Save_Best('displacement_only')
afpo.Clean_Directory()