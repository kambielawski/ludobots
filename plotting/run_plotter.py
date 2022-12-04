import matplotlib.pyplot as plt

class RunPlotter:
    def __init__(self):
        pass

    # TODO: Rewrite this to take a particular run 
    def Rainbow_Waterfall_Plot(self, yaxis='fitness'):
        '''
        Use population data over time to track lineages
        '''
        if self.objective == 'tri_fitness' and yaxis == 'empowerment':
            raise ValueError("Can't plot empowerment under tri-fitness conditions")

        lineages = {} # Indexed by tuple (generation, root parent ID)

        # Setup lineages data structure
        for g, generation in enumerate(self.populationOverTime):
            for individual in generation:
                _, _, fitness, empowerment, lineage = individual

                # Select metric we're looking at
                if self.objective == 'tri_fitness':
                    metric = fitness[1]
                elif self.objective == 'emp_fitness':
                    if yaxis == 'fitness':
                        metric = fitness
                    elif yaxis == 'empowerment':
                        metric = empowerment

                if not metric:
                    raise ValueError("Invalid objective or yaxis value")
            
                if lineage in lineages:
                    # Only add to lineage list if fitness is higher for that gen
                    better_exists = False
                    for g_curr, m in lineages[lineage]:
                        if g == g_curr:
                            if empowerment > metric:
                                lineages[lineage].remove((g_curr, m))
                            else:
                                better_exists = True

                    # Add the current individual to the current max lineage
                    if better_exists == False:
                        lineages[lineage].append((g, metric))
                else:
                    lineages[lineage] = [(g, metric)]

        # Plot each lineage as a line
        for lineage in lineages: 
            plt.step(*zip(*lineages[lineage]))
        plt.title('Lineages (N={}, G={})'.format(self.popSize, self.totalGens))
        plt.xlabel('Generation')
        plt.ylabel('{}'.format((yaxis)))
        plt.savefig('./plots/rainbow_waterfall_{metric}_n{popsize}g{gens}_{objective}.png'
                    .format(metric=yaxis, popsize=self.popSize, gens=self.totalGens, objective=self.objective))
