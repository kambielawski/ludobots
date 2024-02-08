class NNDF: 

    def __init__(self):
        pass

    def Save_Start_Tag(self, file):

        file.write('<neuralNetwork>\n')

    def Save_End_Tag(self, file):

        file.write('</neuralNetwork>')

