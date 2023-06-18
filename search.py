from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO():
    return {
        'name': 'boxdisplacement-emp',
        'morphology': 'biped',
        'task_environment': './task_environments/world.sdf',
        'generations': 100,
        'target_population_size': 30,
        'motor_measure': 'VELOCITY', # 'VELOCITY' or 'DESIRED_ANGLE'
        'objectives': ['displacement'], 
        'empowerment_window_size': 500,
    }

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

afpo.Save_Best('./best_robots/biped')
afpo.Clean_Directory()