class NNDF: 

    def __init__(self, file):
        self.file = file
        pass

    def Save_Start_Tag(self):

        self.file.write('<neuralNetwork>\n')

    def Save_End_Tag(self):

        self.file.write('</neuralNetwork>')

