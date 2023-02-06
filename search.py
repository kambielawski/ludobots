from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
        'generations': 20,
        'target_population_size': 50,
        'motor_measure': 'VELOCITY', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['box_displacement', 'empowerment'], # 'tri_fitness'
        'empowerment_window_size': c.TIMESTEPS // 2,
        'batching': True,
        'batch_size': 5
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

