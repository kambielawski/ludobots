import sys
sys.path.append('C:\\Users\\Kam\\Documents\\dev\\ludobots\\.env\\Lib\\site-packages')
import pybullet as p

from pyrosim.nndf import NNDF

from pyrosim.linksdf  import LINK_SDF

from pyrosim.linkurdf import LINK_URDF

from pyrosim.model import MODEL

from pyrosim.sdf   import SDF

from pyrosim.urdf  import URDF

from pyrosim.joint import JOINT

SDF_FILETYPE  = 0

URDF_FILETYPE = 1

NNDF_FILETYPE   = 2

# global availableLinkIndex

# global linkNamesToIndices

def End():

    if filetype == SDF_FILETYPE:

        sdf.Save_End_Tag(f)

    elif filetype == NNDF_FILETYPE:

        nndf.Save_End_Tag()
    else:
        urdf.Save_End_Tag()

    f.close()

def End_Model():

    model.Save_End_Tag(f)

def Get_Touch_Sensor_Value_For_Link(linkName):

    touchValue = -1.0

    desiredLinkIndex = linkNamesToIndices[linkName]

    pts = p.getContactPoints()

    for pt in pts:

        linkIndex = pt[4]

        if ( linkIndex == desiredLinkIndex ):

            touchValue = 1.0

    return touchValue

def Prepare_Link_Dictionary(bodyID):

    global linkNamesToIndices

    linkNamesToIndices = {}

    for jointIndex in range( 0 , p.getNumJoints(bodyID) ):

        jointInfo = p.getJointInfo( bodyID , jointIndex )

        jointName = jointInfo[1]

        jointName = jointName.decode("utf-8")

        jointName = jointName.split("_")

        linkName = jointName[1]

        linkNamesToIndices[linkName] = jointIndex

        if jointIndex==0:

           rootLinkName = jointName[0]

           linkNamesToIndices[rootLinkName] = -1 

def Prepare_Joint_Dictionary(bodyID):

    global jointNamesToIndices

    jointNamesToIndices = {}

    for jointIndex in range( 0 , p.getNumJoints(bodyID) ):

        jointInfo = p.getJointInfo( bodyID , jointIndex )

        jointName = jointInfo[1].decode('UTF-8')

        jointNamesToIndices[jointName] = jointIndex

def Prepare_To_Simulate(bodyID):

    Prepare_Link_Dictionary(bodyID)

    Prepare_Joint_Dictionary(bodyID)

def Send_Cube(file, name="default",pos=[0,0,0],size=[1,1,1]):

    global availableLinkIndex

    global links

    if filetype == SDF_FILETYPE:

        Start_Model(name,pos)

        link = LINK_SDF(name,pos,size)

        links.append(link)
    else:
        link = LINK_URDF(name,pos,size)

        links.append(link)

    link.Save(file)

    if filetype == SDF_FILETYPE:

        End_Model()

    linkNamesToIndices[name] = availableLinkIndex

    availableLinkIndex = availableLinkIndex + 1

def Send_Joint(file, name,parent,child,type,position, jointAxis):

    joint = JOINT(file, name,parent,child,type,position)

    joint.Save(file, jointAxis)

def Send_Motor_Neuron(file, name,jointName):

    file.write('    <neuron name = "' + str(name) + '" type = "motor"  jointName = "' + jointName + '" />\n')

def Send_Sensor_Neuron(file, name,linkName):

    file.write('    <neuron name = "' + str(name) + '" type = "sensor" linkName = "' + linkName + '" />\n')

def Send_Synapse(file, sourceNeuronName , targetNeuronName , weight ):

    file.write('    <synapse sourceNeuronName = "' + str(sourceNeuronName) + '" targetNeuronName = "' + str(targetNeuronName) + '" weight = "' + str(weight) + '" />\n')

 
def Set_Motor_For_Joint(bodyIndex,jointName,controlMode,targetPosition,maxForce):

    p.setJointMotorControl2(

        bodyIndex      = bodyIndex,

        jointIndex     = jointNamesToIndices[jointName],

        controlMode    = controlMode,

        targetPosition = targetPosition,

        force          = maxForce)

def Start_NeuralNetwork(filename):

    global filetype

    filetype = NNDF_FILETYPE

    file = open(filename,"w")

    global nndf

    nndf = NNDF(file)

    nndf.Save_Start_Tag()
    return file

def Start_SDF(filename):

    global availableLinkIndex

    availableLinkIndex = -1

    global linkNamesToIndices

    linkNamesToIndices = {}

    global filetype

    filetype = SDF_FILETYPE

    global f
 
    f = open(filename,"w")

    global sdf

    sdf = SDF()

    sdf.Save_Start_Tag(f)

    global links

    links = []

def Start_URDF(filename):

    global availableLinkIndex

    availableLinkIndex = -1

    global linkNamesToIndices

    linkNamesToIndices = {}

    global filetype

    filetype = URDF_FILETYPE

    file = open(filename,"w")

    global urdf 

    urdf = URDF(file)

    urdf.Save_Start_Tag()

    global links

    links = []

    return file

def Start_Model(modelName,pos):

    global model 

    model = MODEL(modelName,pos)

    model.Save_Start_Tag(f)
