from ageFitnessPareto import AgeFitnessPareto
import constants as c

def Get_Constants_AFPO():
    return {
        'generations': 10,
        'target_population_size': 30,
        'objectives': ['displacement', 'empowerment'], # 'tri_fitness'
        'empowerment_window_size': c.TIMESTEPS,
        'batching': True,
        'batch_size': 5
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

