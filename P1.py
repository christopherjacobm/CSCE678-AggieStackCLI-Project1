import sys
import os.path
import pickle
from collections import OrderedDict


def main():

    # command line arguments
    args = sys.argv

    # given command
    command = " ".join(args[1:])
    # open the log file if exists already, otherwise create one
    logfile = "aggiestack-log.txt"
    if fileExists(logfile):
        logfile = open(logfile, "a")
    else:
        logfile = open(logfile, "w")

    # command length should be atleast 4
    if (len(args) < 4):
        error(command, logfile)
        sys.exit(0)

    if args[1] == "aggiestack":
        # takes care of the config comamnds
        if args[2] == "config":
            if args[3] == "--hardware" and args[4]:
                status = readInputFile(args[4], "hardwareConfiguration.dct")
                if status == "SUCCESS":
                    status = updateCurrentHardware()
                    status = updateTheCacheMapping()
                logfile.write(command + "     " + status +"\n")
            elif args[3] == "--images" and args[4]:
                status = readInputFile(args[4], "imageConfiguration.dct")
                logfile.write(command + "     " + status +"\n")
            elif args[3] == "--flavors" and args[4]:
                status = readInputFile(args[4], "flavorConfiguration.dct")
                logfile.write(command + "     " + status +"\n")
            else:
                error(command, logfile)

        # takes care of the show commands
        elif args[2] == "show":
            if args[3] == "hardware":
                status = showContent("hardwareConfiguration.dct")
                logfile.write(command + "     " + status +"\n")
            elif args[3] == "images":
                status = showContent("imageConfiguration.dct")
                showRacksAndImages()
                logfile.write(command + "     " + status +"\n")
            elif args[3] == "flavors":
                status = showContent("flavorConfiguration.dct")
                logfile.write(command + "     " + status +"\n")
            elif args[3] == "all":
                status = showAll()
                logfile.write(command + "     " + status +"\n")
            else:
                error(command, logfile)
                
        # takes care of the admin commands
        elif args[2] == "admin":
            if args[3] == "show":
                if args[4] == "hardware":
                    # status = showContent("currentHardwareConfiguration.dct")
                    status = showAvailableHardware()
                    logfile.write(command + "     " + status +"\n")
                elif args[4] == "instances":
                    status = showPhysicalServers()
                    logfile.write(command + "     " + status +"\n")
                elif args[4] == "imagecaches":
                    status = cmdShowImageCachesRackName(args[5])
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            elif args[3] == "can_host":
                if len(args) > 4 and args[4] and args[5]:
                    status, canHostVM = canHost(args[4],args[5])
                    if canHostVM:
                        print("Yes")
                    else:
                        print("No")
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            elif args[3] == "evacuate":
                if len(args) > 4 and args[4]:
                    status = evacuate(args[4])
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            elif args[3] == "remove":
                if len(args) > 4 and args[4]:
                    status = removeMachine(args[4])
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            elif args[3] == "add":
                if len(args) > 14 and args[4] == "--mem" and args[5] and args[6]=="--disk" and args[7] and args[8]=="--vcpus" and args[9] and args[10]=="--ip" and args[11] and args[12]=="--rack" and args[13] and args[14]:
                    status = addMachine([args[5],args[7],args[9],args[11],args[13],args[14]])
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            else:
                error(command, logfile)

        elif args[2] == "server":   #aggiestack server create --image IMAGE --flavor FLAVOR_NAME INSTANCE_NAME
            if args[3] == "create":
                if args[4] == "--image" and args[5] and args[6] == "--flavor" and args[7] and args[8]:
                   print ("Here")
                   status = createInstance(args[5], args[7] , args[8] ) 
                   logfile.write(command + "     " + status +"\n")     
            elif args[3] == "list":
                status = instancesList()
                logfile.write(command + "     " + status +"\n")

            elif args[3] == "delete" and args[4]:
                status = deleteInstance(args[4])
                logfile.write(command + "     " + status +"\n")

            else:
                error(command, logfile)
        else:
            error(command, logfile)
    else:
        error(command, logfile)

# print error
def error(command, logfile):
    logfile.write(command + "     FAILURE" +"\n")
    print("Not a valid command \n", file=sys.stderr)
    helpMessage()
    return 

# print help message
def helpMessage():
    print("Below are the only valid commands for this program:")
    print("aggiestack config --hardware <file name>\naggiestack config -–images <file name>\n"\
    "aggiestack config --flavors <file name>'\naggiestack show hardware\n"\
    "aggiestack show images\naggiestack show flavors\naggiestack show all\n"\
    "aggiestack admin show hardware\naggiestack admin can_host <machine name> <flavor>")

# check if the given file exits 
def fileExists(fileName):
    # get the current working directory
    cwd = os.getcwd()
    filePath = cwd + "/" + fileName

    if os.path.isfile(filePath):
        return True
    else:
        return False

# print the hardware config info
def printMachineHardwareDict(config, fileToRead):

    # read a list for the hardware
    #  read a dict for all other files
    if fileToRead == 'hardwareConfiguration.dct':
        for dict in config:
            print(dict)
    else:
        for machine, configuration in config.items():
            print('%s : %s' % (machine, configuration))


def fileNotEmpty(fileName):
    cwd = os.getcwd()

    if (os.path.getsize(cwd + "/" + fileName) > 0):
        return True
    else:
        return False

"""
Reads the given file and 
save the content into a file
"""
def readInputFile(fileToRead, savedFile):
    status = "FAILURE"

    # a dictionary to store only one instance's config
    config = {}

    # a list to store all the machines in a rack
    machines_config = {}

    # a dcit to store all the machines for each rack
    racks_config = {}

    contentList = {}

    startIndex = 1



    # chekc if the file exists
    fileExist= fileExists(fileToRead)
    
    if fileExist:

        hardware = ["rack", "ip", "mem", "num-disks", "num-vcpus"]
        image = ["image-size-MB", "path"]
        flavor = ["mem", "num-disks", "num-vcpus"]

        if (savedFile == "hardwareConfiguration.dct"):
            listToLoop = hardware
        elif (savedFile == "imageConfiguration.dct"):
            listToLoop = image
        else:
            listToLoop = flavor

        # open the input file to read
        f = open(fileToRead, "r")
        lines = f.readlines()

        if fileExists(savedFile) and fileNotEmpty(savedFile):
            with open(savedFile, "rb") as f:
                contentList = pickle.load(f)

        # only done for the racks hardware
        if listToLoop == hardware:
            # read the racks data
            numberOfRacks = int(lines[0])

            for line in lines[1:numberOfRacks + 1]:
                racks = line.split()
                    
                racks_config[racks[0]] = {"mem": racks[1]}

            startIndex = numberOfRacks + 2

    
        for line in lines[startIndex:]:
            tokens = line.split()
            
            for i, val in enumerate(listToLoop):
                config[val] = tokens[i+1]

            if listToLoop == hardware:
                machines_config[tokens[0]] = config
            else:
                contentList[tokens[0]] = config
            config = {}

        if listToLoop == hardware:
            contentList = []
            contentList.append(racks_config)
            contentList.append(machines_config)

        with open(savedFile, "wb") as f:
            pickle.dump(contentList, f)

        status = "SUCCESS"

    else:
        print("Given file does not exist")

    return status


"""
showContent method - sub-method
Used in various methods
"""
def showContent(fileToRead):
    status = "SUCCESS"

    if fileExists(fileToRead) and fileNotEmpty(fileToRead):
        with open(fileToRead, "rb") as f:
            config = pickle.load(f)
 
        # configDict = OrderedDict(sorted(config.items(), key=lambda x: x[0]))
    
        printMachineHardwareDict(config, fileToRead)

    else:
        print("No information available")
    return status
    

"""
showAll - Used in show -all
Giving the statistics of all the resources
"""
def showAll():
    status = "SUCCESS"

    print("Hardware Info: \n")
    showContent("hardwareConfiguration.dct")
    print("Image Info: \n")
    showContent("imageConfiguration.dct")
    print("Flavor Info: \n")
    showContent("flavorConfiguration.dct")

    return status
    
    
"""
updateCurrentHardware - Updates currentHardwareConfiguration.dct whenever hardwareConfiguration.dct is updated 
TODO: handle all cases when vCPUs can be allocated, as some entries should not be overwritten
""" 
def updateCurrentHardware():
    status = "FAILURE"
    hardwareFile = "hardwareConfiguration.dct"
    currHardwareFile = "currentHardwareConfiguration.dct"
    columns = ["rack", "ip", "mem", "num-disks", "num-vcpus"]
    
    # a dictionary to store all the configurations
    currHardwareDict = {}
    
    with open(hardwareFile, "rb") as f:
        hardwareDict = pickle.load(f)

    for config in hardwareDict:
        for key, value in config.items():
            config = {}
            if len(value) > 1:
                for val in columns:
                    config[val] = value[val] 
                    currHardwareDict[key] = config
            else:
                currHardwareDict[key] = {"mem": value["mem"]} 
    
    # save to currHardwareDict
    with open(currHardwareFile, "wb") as f:
        pickle.dump(currHardwareDict, f)
            
        status = "SUCCESS"

    return status

"""
canHost - Checks if a particular machine currently has the resources to host a vCPU of the given flavor, in the currentHardwareDict
"""   
def canHostDict(machineName, flavorName, currentHardwareDict):
    status = "FAILURE"
    flavorFile = "flavorConfiguration.dct"
    columns = ["mem", "num-disks", "num-vcpus"]
    
    if fileExists(flavorFile) and fileNotEmpty(flavorFile):
        with open(flavorFile, "rb") as f:
           flavorDict = pickle.load(f)
        # find the correct machine and flavor
        if (flavorName in flavorDict) and (machineName in currentHardwareDict):
            status = "SUCCESS"
            # check if the number of resources required is <= those available
            for val in columns:
                if int(flavorDict[flavorName][val]) > int(currentHardwareDict[machineName][val]):
                    return status, False
            return status, True
        else:
            print("Record not found")
            return status, False
    
"""
canHost - Checks if a particular machine currently has the resources to host a vCPU of the given flavor
"""     
def canHost(machineName, flavorName):
    status = "FAILURE"
    
    currHardwareFile = "currentHardwareConfiguration.dct"
    
    if  fileExists(currHardwareFile) and fileNotEmpty(currHardwareFile):
        # retrieve the flavor and current hardware dicts from their files
        with open(currHardwareFile, "rb") as f:
            currentHardwareDict = pickle.load(f)
        return canHostDict(machineName, flavorName, currentHardwareDict)    
    else:
        print("No information available")
        return status, False   

# create an instance if it does not exist
# Give error if the instance already exits
def createInstance(imageName, flavorName, instanceName):
    status = "FAILURE"

    columns = ["image", "flavor", "machine"]

    # dictionary for the new instances
    newInstance = {}
    # dictionary for the existing instances
    instancesDict = {}

    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        # load the existing instances
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)

            # return an error if the instance requested already exits
            if instanceExits(instanceName, instancesDict):
                print("The given instance already exists.")
                return status


    # check if the given image exits
    if not imageExists(imageName):
        print("The given image does not exist.")
        return status

    # check if the given flavor exits
    if not flavorExists(flavorName):
        print("The given flavor does not exist.")
        return status

    machineName = findMachine(imageName, flavorName)
    if machineName == "":
        print("Resources not available to fulfil this request.")
        return status

    status = "SUCCESS"

    requestedInstance = [imageName, flavorName, machineName]

    # create a dictionary for the new instance
    for i, item in enumerate(columns):
        newInstance[item] =  requestedInstance[i]

    instancesDict[instanceName] = newInstance

     # save the instances back in the file
    with open(instancesFile, "wb") as f:
        pickle.dump(instancesDict, f)


    updateCaching(machineName, imageName)
    # update the machine configs
    updateResources(machineName, flavorName, 'createInstance')

    return status

# returns true if the instance already exists
def instanceExits(instanceName, instancesDict):
    if instanceName in instancesDict.keys():
        return True
    return False

# returns true if the image exits
def imageExists(imageName):
    imagesFile = 'imageConfiguration.dct'

    if fileExists(imagesFile) and fileNotEmpty(imagesFile):
        with open(imagesFile, "rb") as f:
            imagesDict = pickle.load(f)

            if imageName in imagesDict.keys():
                return True
    return False

# returns true if the flavor exits
def flavorExists(flavorName):
    flavorsFile = 'flavorConfiguration.dct'

    if fileExists(flavorsFile) and fileNotEmpty(flavorsFile):
        with open(flavorsFile, "rb") as f:
            flavorsDict = pickle.load(f)

            if flavorName in flavorsDict.keys():
                return True
    return False
    
# returns true if the machine exists in hardwareConfiguration.dct
def machineExistsInHardwareConfig(machineName, hardwareConfigDict):
    if machineName in hardwareConfigDict[1].keys():
        return True
    return False
    
# returns true if the machine exists in currentHardwareConfiguration.dct
def machineExistsInCurrentHardwareConfig(machineName, currentHardwareConfigDict):
    if machineName in currentHardwareConfigDict.keys():
        return True
    return False
    
# find the machine to host a virutal instance
def findMachine(imageName, flavorName):
    machineName = ""

    hardwareFile = 'currentHardwareConfiguration.dct'

    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

        found, machineName = tryIntelligentSelection(imageName, flavorName)
        if found:
            return machineName

        machines = [_ for _ in hardwareList.items() if len(_[1]) > 1]
        sortedMachines = sortMachinesByRackStorageAvailable(machines)
        for key, value in sortedMachines:
            # only check the machines and not racks
            if len(value) > 1:
                _, canHostVM = canHost(key, flavorName)
                if canHostVM:
                    return key

    return machineName

# updates the machine resources dict (currentHardwareDict), but does not write to file
# action: createInstance - subtract resources
# action: deleteInstance - add resources    
def updateResourcesDict(machineName, flavorName, action,currentHardwareDict):
    flavorFile = "flavorConfiguration.dct"
    columns = ["mem", "num-disks", "num-vcpus"]
     
    if fileExists(flavorFile)  and  fileNotEmpty(flavorFile):
        with open(flavorFile, "rb") as f:
            flavorDict = pickle.load(f)
            
        m = currentHardwareDict[machineName]
        f = flavorDict[flavorName]

        # update the resources
        for val in columns:
            if action == 'createInstance':
                newValue = int(m[val]) - int(f[val])
            else:
                newValue = int(m[val]) + int(f[val])

            currentHardwareDict[machineName][val] = newValue
            
# update the machine resources when creating a new instance
# action: createInstance - subtract resources
# action: deleteInstance - add resources
def updateResources(machineName, flavorName, action):
    currHardwareFile = "currentHardwareConfiguration.dct"


    if fileExists(currHardwareFile) and fileNotEmpty(currHardwareFile):
        # retrieve the flavor and current hardware dicts from their files
        with open(currHardwareFile, "rb") as f:
            currentHardwareDict = pickle.load(f)
            
        updateResourcesDict(machineName, flavorName, action, currentHardwareDict)

        with open(currHardwareFile, "wb") as f:
            pickle.dump(currentHardwareDict, f)

# returns a list of all the running instances
# command: aggiestack server list
def instancesList():
    status = "FAILURE"
    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)
        
        for instance, configuration in instancesDict.items():
            els = list(configuration.items())

            print("name : ", instance, " ", end='')
            for i in range(len(els)):
                print(els[i],  " ", end='')

            print()

        status = 'SUCCESS'

    else:
        print("No information available")

    return status

# command: aggiestack admin show hardware
def showAvailableHardware():
    status = "FAILURE"
    currHardwareFile = "currentHardwareConfiguration.dct"
    
    if fileExists(currHardwareFile) and fileNotEmpty(currHardwareFile):
        with open(currHardwareFile, "rb") as f:
            currentHardwareDict = pickle.load(f)

        for key, value in currentHardwareDict.items():
            print (key, value)
            # only print the machines and not racks
            if len(value) > 1:
                print('%s : %s' % (key, value))
        status = 'SUCCESS'

    else:
        print("No information available.")
    return status

# aggiestack admin show instances
# For each instance currently running, 
# it shows where (which physical server) the instance is running
def showPhysicalServers():
    status = "FAILURE"

    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)

        for instance, configuration in instancesDict.items():
            print('%s : %s' % (instance, configuration["machine"]))

        status = "SUCCESS"

    else:
        print("No information available.")

    return status

# aggiestack server delete INSTANCE_NAME
def deleteInstance(instanceName):

    status = 'FAILURE'

    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        # load the existing instances
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)

            if instanceExits(instanceName, instancesDict):
                status = 'SUCCESS'

                # update the machine resources
                machineName = instancesDict[instanceName]["machine"]
                flavorName = instancesDict[instanceName]["flavor"]
                updateResources(machineName, flavorName, 'deleteInstance')

                # delete the instance from the instances dictionary
                del instancesDict[instanceName]

                # save the updated instance file
                with open(instancesFile, "wb") as f:
                    pickle.dump(instancesDict, f)
            else:
                print("Given instance does not exist")

    else:
        print("Given instance does not exist")
    return status
    
# Moves an instance to a new machine, does not save dicts to files 
def migrateInstance(instance, newMachine, instancesDict, currentHardwareDict):
    #modify instance file entry
    oldMachine = instancesDict[instance]['machine']
    instancesDict[instance]['machine'] = newMachine
    
    #updateResources deleteInstance
    updateResourcesDict(oldMachine, instancesDict[instance]['flavor'], 'deleteInstance',currentHardwareDict)
    
    #updateResource createInstance
    updateResourcesDict(newMachine, instancesDict[instance]['flavor'], 'createInstance',currentHardwareDict)
    
# aggiestack admin evacuate RACK_NAME
# Moves all the servers on this rack to machines on another rack, if possible
def evacuate(rackName):
    status = 'FAILURE'
    
    # separate machines into those on this rack and those on other racks
    file = 'currentHardwareConfiguration.dct'
    if fileExists(file) and fileNotEmpty(file):
        with open(file, "rb") as f:
            currentHardwareConfigDict = pickle.load(f)
            
            evacuationRackMachines = []
            otherRacksMachines = []
            
            for machine, configuration in currentHardwareConfigDict.items():
                
                if len(configuration)>1:
                    if configuration["rack"] == rackName:
                        evacuationRackMachines.append(machine)
                    else:
                        otherRacksMachines.append(machine)
                    
    #find the instances which are on machines on the given rack
    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)
        
        for instance, configuration in instancesDict.items():
            if configuration['machine'] in evacuationRackMachines:
                #for each instance, find a machine which can host it, in otherRacksMachines
                canHostVM = False
                for newMachine in otherRacksMachines:
                    _, canHostVM = canHostDict(newMachine,configuration['flavor'],currentHardwareConfigDict)
                    if canHostVM:
                        migrateInstance(instance, newMachine, instancesDict, currentHardwareConfigDict)
                        break
                if not canHostVM:
                    print("The machines available are not capable of hosting these instances")
                    return status
                    
    # save the updated instance file
    with open(instancesFile, "wb") as f:
        pickle.dump(instancesDict, f)

    with open(file, "wb") as f:
        pickle.dump(currentHardwareConfigDict, f)
                    
    status = 'SUCCESS'
    
    return status
    
# aggiestack admin remove MACHINE
# Removes a machine, making sure there is no instance currently on it
 
def removeMachine(machineName):
    status = 'FAILURE'
    foundInHardwareConfig = False
    
    # Check if there is an instance running on this machine
    instancesFile = "instancesRunning.dct"
    if fileExists(instancesFile) and fileNotEmpty(instancesFile):
        with open(instancesFile, "rb") as f:
            instancesDict = pickle.load(f)
        
        for instance, configuration in instancesDict.items():
            if configuration['machine'] == machineName:
                print("Instance ",instance, " is already running on machine ",machineName)
                return status
                
    #remove this machine from hardwareConfiguration.dct
    file = 'hardwareConfiguration.dct'
    if fileExists(file) and fileNotEmpty(file):
        with open(file, "rb") as f:
            hardwareConfigDict = pickle.load(f)
            
            if machineExistsInHardwareConfig(machineName,hardwareConfigDict):
                foundInHardwareConfig = True
                del hardwareConfigDict[1][machineName]
                with open(file, "wb") as f:
                    pickle.dump(hardwareConfigDict, f)
                                        
    #remove this machine from currentHardwareConfiguration.dct              
    file = 'currentHardwareConfiguration.dct'
    if fileExists(file) and fileNotEmpty(file):
        with open(file, "rb") as f:
            currentHardwareConfigDict = pickle.load(f)
            
            if machineExistsInCurrentHardwareConfig(machineName,currentHardwareConfigDict):
                del currentHardwareConfigDict[machineName]
                with open(file, "wb") as f:
                    pickle.dump(currentHardwareConfigDict, f)
            elif not foundInHardwareConfig:
                print("Machine not found! ")
                return status
                    
    status = 'SUCCESS'
    
    return status
    
# aggiestack admin add –-mem MEM –disk NUM_DISKS –vcpus VCPUs –ip IP –rack RACK_NAME MACHINE
# Adds a machine
def addMachine(argsList): #argsList -> [mem,numDisks,vCPUs,ip,rackName,machineName]
    status = 'FAILURE'
    
    machineName = argsList[5]  
  
    columns = ["mem", "num-disks", "num-vcpus", "ip","rack"]
    
    # Create a dict for the new machine
    machineDict ={}
    for i in range(len(columns)):
        machineDict[columns[i]] = argsList[i]

    hcFile = 'hardwareConfiguration.dct'
    if fileExists(hcFile) and fileNotEmpty(hcFile):
        with open(hcFile, "rb") as f:
            hardwareConfigDict = pickle.load(f)
            
    chcFile = 'currentHardwareConfiguration.dct'
    if fileExists(chcFile) and fileNotEmpty(chcFile):
        with open(chcFile, "rb") as f:
            currentHardwareConfigDict = pickle.load(f)
                        
    if machineExistsInHardwareConfig(machineName,hardwareConfigDict) or machineExistsInCurrentHardwareConfig(machineName,currentHardwareConfigDict):
        print("A machine with this name already exists!")
        return status     
    
    # Add this machine to hardwareConfiguration.dct
    hardwareConfigDict[1][machineName] = machineDict
    with open(hcFile, "wb") as f:
        pickle.dump(hardwareConfigDict, f)
    
    # Add this machine to currentHardwareConfiguration.dct         
    currentHardwareConfigDict[machineName] = machineDict
    with open(chcFile, "wb") as f:
        pickle.dump(currentHardwareConfigDict, f)
                    
    status = 'SUCCESS'
    
    return status

def sortMachinesByRackStorageAvailable(machines):
    hardwareFile = 'currentHardwareConfiguration.dct'
    hardwareList = {}
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)
    
    return sorted(machines, reverse=True, key = lambda x:int(hardwareList[x[1]['rack']]['mem']))

def rackExists(rackName):
    hardwareFile = 'currentHardwareConfiguration.dct'
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

        for key, value in hardwareList.items():
            # only check the racks and not machines
            if len(value) == 1:
                if key == rackName:
                    return True
    return False


def cmdShowImageCachesRackName(rackName):

    if not rackExists(rackName):
        print ("Rack does not exist")
        return "FAILURE"

    allImages = getImagesOnRack(rackName)
    currentCapacity = getSpaceOnRack(rackName)
    print ("List of images on this rack are: ")
    for img in allImages:
        print (img,)
    print ("Available Storage Space on this rack is:")
    print (currentCapacity)
    return "SUCCESS"



def isImageCached(imageName):
    cacheFile = 'cachedImagesToRackMapping.dct'
    imageToRackMap = {}
    if not fileExists(cacheFile):
        with open(cacheFile, "wb") as f:
            pickle.dump(imageToRackMap, f)
        
    with open(cacheFile, "rb") as f:
        imageToRackMap = pickle.load(f)

    return imageName in imageToRackMap.keys()

def tryIntelligentSelection(imageName, flavorName):
    isChached = isImageCached(imageName)
    if not isChached:
        return False, ""
    
    cacheFile = 'cachedImagesToRackMapping.dct'
    imageToRackMap = {}
    with open(cacheFile, "rb") as f:
        imageToRackMap = pickle.load(f)

    racksList = imageToRackMap[imageName]
    hardwareFile = 'currentHardwareConfiguration.dct'
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

        for key, value in hardwareList.items():
            # only check the machines and not racks
            if len(value) > 1:
                _, canHostVM = canHost(key, flavorName)
                if value['rack'] in racksList and canHostVM:
                    return True, key

    return False, ""

def updateCaching(machineName, imageName):
    hardwareFile = 'currentHardwareConfiguration.dct'
    hardwareList = {}
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

    cacheFile = 'cachedImagesToRackMapping.dct'
    imageToRackMap = {}
    with open(cacheFile, "rb") as f:
        imageToRackMap = pickle.load(f)
    
    if imageName not in imageToRackMap.keys():
        imageToRackMap[imageName] = []
    imageToRackMap[imageName].append(hardwareList[machineName]['rack'])
    
    requiredSpace = 0
    imagesFile = 'imageConfiguration.dct'
    imagesDict = {}
    if fileExists(imagesFile) and fileNotEmpty(imagesFile):
        with open(imagesFile, "rb") as f:
            imagesDict = pickle.load(f)
    
    if imageName in imagesDict.keys():
        requiredSpace = int(imagesDict[imageName]['image-size-MB'])

    imagesOnRack = getImagesOnRack(hardwareList[machineName]['rack'])
    if imageName not in imagesOnRack:
        n = len(imagesOnRack)
        i = 0
        while i < n and int(hardwareList[hardwareList[machineName]['rack']]['mem']) < requiredSpace:
            if imagesOnRack[i] in imagesDict.keys():
                hardwareList[hardwareList[machineName]['rack']]['mem'] = int(hardwareList[hardwareList[machineName]['rack']]['mem']) + int(imagesDict[imagesOnRack[i]]['image-size-MB'])
            i += 1
        j = 0
        while j < i:
            imageToRackMap[imagesOnRack[j]].remove(hardwareList[machineName]['rack'])
            j += 1

        hardwareList[hardwareList[machineName]['rack']]['mem'] = int(hardwareList[hardwareList[machineName]['rack']]['mem']) - requiredSpace
    print (hardwareList[machineName]['rack'], hardwareList[hardwareList[machineName]['rack']]['mem'])

    with open(cacheFile, "wb") as f:
        pickle.dump(imageToRackMap, f)

    with open(hardwareFile, "wb") as f:
        pickle.dump(hardwareList, f)

def showRacksAndImages():
    hardwareFile = 'currentHardwareConfiguration.dct'
    hardwareList = {}
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

    for key, value in hardwareList.items():
        if len(value) == 1:
            print (key, getImagesOnRack(key))


def getImagesOnRack(rackName):
    cacheFile = 'cachedImagesToRackMapping.dct'
    imageToRackMap = {}
    with open(cacheFile, "rb") as f:
        imageToRackMap = pickle.load(f)
    
    ans = []
    for key, value in imageToRackMap.items():
        if rackName in value:
            ans.append(key)
    
    return ans

def getSpaceOnRack(rackName):
    hardwareFile = 'currentHardwareConfiguration.dct'
    hardwareList = {}
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareList = pickle.load(f)

    return hardwareList[rackName]['mem']

def updateTheCacheMapping():
    cacheFile = 'cachedImagesToRackMapping.dct'
    # a dictionary to store all image->rack_list map
    imageToRackMap = {}
    
    if not fileExists(cacheFile):
        with open(cacheFile, "wb") as f:
            pickle.dump(imageToRackMap, f)

    return "SUCCESS"

if __name__ == "__main__":
    main()



# Bonus Part
# 1. show image: each rack which images
# 2. image flavor instance : consider cached rack
# 3. image cache rack name : images on rack and availabe space on rack