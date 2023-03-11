from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
        'generations': 100,
        'target_population_size': 20,
        'motor_measure': 'DESIRED_ANGLE', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['empowerment'], # 'tri_fitness'
        'empowerment_window_size': c.TIMESTEPS // 2,
        'batching': True,
        'batch_size': 5
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

