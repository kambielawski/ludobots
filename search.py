from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO():
    return {
        'generations': 5,
        'target_population_size': 10,
        'objective': 'emp_fitness', # 'tri_fitness'
        'batching': True,
        'batch_size': 5
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

