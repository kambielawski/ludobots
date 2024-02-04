from ageFitnessPareto import AgeFitnessPareto

def Get_Constants_AFPO():
    return {
        'name': 'quadruped2x_multisim_displacement_mD',
        'morphology': 'quadruped',
        'generations': 50,
        'n_runs': 15,
        'target_population_size': 30,
        'motor_measure': 'DESIRED_ANGLE',
        'empowerment_window_size': 500,
        'wind': 0,
        'simulations': [
            {
                'task_environment': './task_environments/world.sdf',
                'objectives': ['displacement', 'empowerment'],
                'body_orientation': 0
            },
            {
                'task_environment': './task_environments/world.sdf',
                'objectives': ['displacement', 'empowerment'],
                'body_orientation': 1
            },
            {
                'task_environment': './task_environments/world.sdf',
                'objectives': ['displacement', 'empowerment'],
                'body_orientation': 2
            },
        ]
}

# Age-Fitness Pareto Optimization
afpo = AgeFitnessPareto(Get_Constants_AFPO())
afpo.Evolve()

afpo.Save_Best('./best_robots/quadruped2x/displacement-empowerment')
afpo.Clean_Directory()