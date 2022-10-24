from plotter import Plotter

p = Plotter()

p.Parse_Gen_Data('../data/gen_data.txt')
p.Print_Top_Fitness()

p.Rainbow_Waterfall_Plot()
