import pickle

class ExperimentPlotter:
    def __init__(self, dir):
        self.runs = {}
        if dir: # Continue existing experiment
            self.pickle_file = f'{dir}/evo_runs.pickle'
            with open(self.pickle_file, 'rb') as pf:
                self.runs = pickle.load(pf)
                self.t1 = list(self.runs.keys())[0]
                self.t2 = list(self.runs.keys())[1]
        else: # Initialize a new experiment
            raise ValueError("Experiment directory needs to be specified.")
        
    def Top_Fitness_95CI(self):
        # Load data into a data structure
        self.popData = {self.t1: [], self.t2: []}
        for treatment in self.runs:
            for afpo in self.runs[treatment]:
                self.popData[treatment].append(self.runs[treatment][afpo].plotter.Get_Population_Data())

        for treatment in self.runs:
            for afpo in self.runs[treatment]:
                print(f'Current gen: {self.runs[treatment][afpo].currentGen}')

        # print(self.runs[self.t1][0].plotter.Get_Population_Data()[0])
        fitness = {
            self.t1: {g: [] for g in self.popData[self.t1][0]},
            self.t2: {g: [] for g in self.popData[self.t2][0]}
        }
        for treatment in self.popData:
            for run in self.popData[treatment]:
                for generation in run: # Each is an evo run
                    pass
                    # print(generation)
        # Y-vals: get top fitness from each run
        fitness = {
            self.t1: {g: None for g in self.popData[self.t1][0]}, 
            self.t2: {g: None for g in self.popData[self.t2][0]}
        }

        print(fitness)

        for treatment in self.runs:
            for afpo in self.runs[treatment]:
                for gen in self.runs[treatment][afpo]:
                    fitness[treatment][afpo].append(max(self.popData[treatment][afpo][gen], key=lambda x: x[2]))
        # t1_y = [afpo.Top_Fitness() for afpo in self.runs[self.t1]]
        # t2_y = [afpo.Top_Fitness() for afpo in self.runs[self.t2]]
        print(fitness)

        # X-vals: generations

exp_plotter = ExperimentPlotter('./experiments/exp_Nov08_01_25')
exp_plotter.Top_Fitness_95CI()