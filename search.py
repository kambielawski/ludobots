from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
        'generations': 50,
        'target_population_size': 50,
        'motor_measure': 'DESIRED_ANGLE', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['displacement'], # 'tri_fitness'
        'empowerment_window_size': c.TIMESTEPS // 2,
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

afpo.Save_Best('displacement_only')
afpo.Clean_Directory()