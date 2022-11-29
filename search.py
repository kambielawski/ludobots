from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO():
    return {
        'generations': 10,
        'target_population_size': 30,
        'objective': 'emp_fitness', # 'tri_fitness'
        'batching': True,
        'batch_size': 5
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

