from plotter import Plotter

p = Plotter()

p.Parse_Gen_Data('../data/gen_data.txt')
print(p.Get_Top_Fitness())

p.Rainbow_Waterfall_Plot()
