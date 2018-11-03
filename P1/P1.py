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
                # if status == "SUCCESS":
                #     status = updateCurrentHardware()
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
                    status = showContent("currentHardwareConfiguration.dct")
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
            elif args[3] == "can_host":
                if len(args) > 4 and args[4] and args[5]:
                    status = canHost(args[4],args[5])
                    logfile.write(command + "     " + status +"\n")
                else:
                    error(command, logfile)
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

         # a dictionary to store all the configurations
        if listToLoop == hardware:
            contentList = []
        else:
            contentList = {}

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
    columns = ["mem", "num-disks", "num-vcpus"]
    
    # a dictionary to store all the configurations
    currHardwareDict = {}
    
    if fileExists(hardwareFile) and fileNotEmpty(hardwareFile):
        with open(hardwareFile, "rb") as f:
            hardwareDict = pickle.load(f)

        # copy data from one dictionary to the other
        for machineName, machineInfo in hardwareDict.items():
            config = {}
            for val in columns:
                config[val] = machineInfo[val] 
    
            currHardwareDict[machineName] = config
        
        # save to currHardwareDict
        with open(currHardwareFile, "wb") as f:
            pickle.dump(currHardwareDict, f)
            
        status = "SUCCESS"
    else:
        print("No information available")
    return status


"""
canHost - Checks if a particular machine currently has the resources to host a vCPU of the given flavor
"""     
def canHost(machineName, flavorName):
    status = "FAILURE"
    flavorFile = "flavorConfiguration.dct"
    currHardwareFile = "currentHardwareConfiguration.dct"
    columns = ["mem", "num-disks", "num-vcpus"]
    
    if fileExists(flavorFile)  and fileExists(currHardwareFile) and fileNotEmpty(flavorFile) and fileNotEmpty(currHardwareFile):
		# retrieve the flavor and current hardware dicts from their files
        with open(flavorFile, "rb") as f:
            flavorDict = pickle.load(f)
        with open(currHardwareFile, "rb") as f:
            currentHardwareDict = pickle.load(f)
        
		# find the correct machine and flavor
        if (flavorName in flavorDict) and (machineName in currentHardwareDict):
            status = "SUCCESS"
			# check if the number of resources required is <= those available
            for val in columns:
                if int(flavorDict[flavorName][val]) > int(currentHardwareDict[machineName][val]):
                    print("No")
                    return status
            print("Yes")
        else:
            print("Record not found")
    else:
        print("No information available")
    return status   


# def readInputFile(fileToRead, savedFile):
#     status = "FAILURE"

#     # a dictionary to store all the configurations
#     contentList = {}

#     # a dictionary to store only one instance's config
#     config = {}

#     # chekc if the file exists
#     fileExist= fileExists(fileToRead)
    
#     if fileExist:

#         hardware = ["ip", "mem", "num-disks", "num-vcpus"]
#         image = ["path"]
#         flavor = ["mem", "num-disks", "num-vcpus"]

#         if (savedFile == "hardwareConfiguration.dct"):
#             listToLoop = hardware
#         elif (savedFile == "imageConfiguration.dct"):
#             listToLoop = image
#         else:
#             listToLoop = flavor

#         # open the input file to read
#         f = open(fileToRead, "r")
#         lines = f.readlines()

#         if fileExists(savedFile) and fileNotEmpty(savedFile):
#             with open(savedFile, "rb") as f:
#                 contentList = pickle.load(f)

#         # save the file data
#         for line in lines[1:]:
#             tokens = line.split()
            
#             for i, val in enumerate(listToLoop):
#                 config[val] = tokens[i+1]
            
#             contentList[tokens[0]] = config
#             config = {}
            

#         with open(savedFile, "wb") as f:
#             pickle.dump(contentList, f)

#         status = "SUCCESS"

#     else:
#         print("Given file does not exist")

#     return status       

if __name__ == "__main__":
    main()