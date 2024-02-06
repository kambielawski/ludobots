class URDF:

    def __init__(self, file):

        self.depth = 0
        self.file = file

    def Save_Start_Tag(self):

        self.file.write('<robot name="robot">\n')

    def Save_End_Tag(self):

        self.file.write("</robot>")
