from pyrosim.neuron  import NEURON

from pyrosim.synapse import SYNAPSE

class NEURAL_NETWORK: 

    def __init__(self,nndfFileName):

        self.neurons = {}

        self.synapses = {}

        self.sensor_links = []

        f = open(nndfFileName,"r")

        for line in f.readlines():

            self.Digest(line)

        f.close()

    def Print(self):

        self.Print_Sensor_Neuron_Values()

        self.Print_Hidden_Neuron_Values()

        self.Print_Motor_Neuron_Values()

        print("")
    
    def Get_Neuron_Names(self):
        return self.neurons.keys()

    def Is_Motor_Neuron(self, neuronName):
        return self.neurons[neuronName].Is_Motor_Neuron()

    def Get_Motor_Neurons_Joint(self, neuronName):
        return self.neurons[neuronName].Get_Joint_Name()

    def Get_Value_Of(self, neuronName):
        return self.neurons[neuronName].Get_Value()
    
    def Is_Sensor_Link(self, linkName):
        if linkName in self.sensor_links:
            return True

    def Update(self):
        for n in self.neurons:
            if self.neurons[n].Is_Sensor_Neuron():
                self.neurons[n].Update_Sensor_Neuron()
            else:
                self.neurons[n].Update_Hidden_Or_Motor_Neuron(self.neurons, self.synapses)
            # print(self.neurons[n].Get_Value())

# ---------------- Private methods --------------------------------------

    def Add_Neuron_According_To(self,line):

        neuron = NEURON(line)

        self.neurons[ neuron.Get_Name() ] = neuron

        if neuron.Is_Sensor_Neuron():
            self.sensor_links.append( neuron.Get_Link_Name() )

    def Add_Synapse_According_To(self,line):

        synapse = SYNAPSE(line)

        sourceNeuronName = synapse.Get_Source_Neuron_Name()

        targetNeuronName = synapse.Get_Target_Neuron_Name()

        self.synapses[sourceNeuronName , targetNeuronName] = synapse

    def Digest(self,line):

        if self.Line_Contains_Neuron_Definition(line):

            self.Add_Neuron_According_To(line)

        if self.Line_Contains_Synapse_Definition(line):

            self.Add_Synapse_According_To(line)

    def Line_Contains_Neuron_Definition(self,line):

        return "neuron" in line

    def Line_Contains_Synapse_Definition(self,line):

        return "synapse" in line

    def Print_Sensor_Neuron_Values(self):

        print("sensor neuron values: " , end = "" )

        for neuronName in sorted(self.neurons):

            if self.neurons[neuronName].Is_Sensor_Neuron():

                self.neurons[neuronName].Print()

        print("")

    def Print_Hidden_Neuron_Values(self):

        print("hidden neuron values: " , end = "" )

        for neuronName in sorted(self.neurons):

            if self.neurons[neuronName].Is_Hidden_Neuron():

                self.neurons[neuronName].Print()

        print("")

    def Print_Motor_Neuron_Values(self):

        print("motor neuron values: " , end = "" )

        for neuronName in sorted(self.neurons):

            if self.neurons[neuronName].Is_Motor_Neuron():

                self.neurons[neuronName].Print()

        print("")
