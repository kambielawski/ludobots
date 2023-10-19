from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO():
    return {
        'name': 'displacement',
        'morphology': 'octoped',
        'task_environment': './task_environments/world.sdf',
        'generations': 50,
        'target_population_size': 20,
        'motor_measure': 'DESIRED_ANGLE', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['displacement', 'empowerment'], 
        'empowerment_window_size': 500,
        'wind': 0
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

afpo.Save_Best('./best_robots/octoped/displacement-empowerment')
afpo.Clean_Directory()