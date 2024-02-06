from pyrosim.commonFunctions import Save_Whitespace

class JOINT: 

    def __init__(self,file, name,parent,child,type,position):

        self.name = name

        self.parent = parent

        self.child  = child

        self.type   = type

        self.position = position

        self.depth = 1
        
        self.file = file

    def Save(self, jointAxis):

        Save_Whitespace(self.depth,self.file)
        self.file.write('<joint name="' + self.name + '" type="' + self.type + '">' + '\n')

        Save_Whitespace(self.depth,self.file)
        self.file.write('   <parent link="' + self.parent + '"/>' + '\n')

        Save_Whitespace(self.depth,self.file)
        self.file.write('   <child  link="' + self.child  + '"/>' + '\n')

        Save_Whitespace(self.depth,self.file)
        originString = str(self.position[0]) + " " + str(self.position[1]) + " " + str(self.position[2])
        self.file.write('   <origin rpy="0 0 0" xyz="' + originString + '" />\n')

        Save_Whitespace(self.depth,self.file)
        self.file.write('   <axis xyz="' + jointAxis + '"/>\n')

        Save_Whitespace(self.depth,self.file)
        self.file.write('   <limit effort="0.0" lower="-3.14159" upper="3.14159" velocity="0.0"/>\n')

        Save_Whitespace(self.depth,self.file)
        self.file.write('</joint>' + '\n')

