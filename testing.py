# Print out text string to console and to ConsoleOutput.txt
def printOut(text):
    print(text)
    global consoleOutputFile
    consoleOutputFile.write(text + "\n")
    consoleOutputFile.flush()

import urllib.request
import json
import csv
from datetime import datetime
import os
import requests

# Start the clock to calculate overall elapsed time
overallStartTime = datetime.now()

# Create Output folder if it doesn't exist
currentDirectory = os.getcwd()
outputDirectory = os.path.join(currentDirectory, r'Output')
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

# Create a folder for this test: Output/Testing-YYYY-MM-DD-HH-MM-SS
folderName = "Testing-" + overallStartTime.strftime("%Y-%m-%d-%H-%M-%S")
dateDirectory = os.path.join(outputDirectory, folderName)
if not os.path.exists(dateDirectory):
    os.makedirs(dateDirectory)
    print("Creating new folder in Output folder: " + folderName)

# Create a file where console output will be saved
fileName = os.path.join(dateDirectory, "ConsoleOutput.txt")
consoleOutputFile = open(fileName, "w")

# Load the test sites from GitHub
with urllib.request.urlopen("https://raw.githubusercontent.com/USGS-WiM/StreamStats-Setup/master/batchTester/testSites.geojson") as url:
    sites = json.loads(url.read().decode())['features']

servers = ["test", "prodweba", "prodwebb"]
resultsFolders = ["BasinDelineations", "BasinCharacteristics", "FlowStatistics"]

for server in servers:
    # Create a folder for server results: Output/Testing-YYYY-MM-DD-HH-MM-SS/[TEST, PRODWEBA, or PRODWEBB]
    serverFolderDirectory = os.path.join(dateDirectory, server.upper())
    if not os.path.exists(serverFolderDirectory):
        os.makedirs(serverFolderDirectory)
    for resultsFolder in resultsFolders:
        # Create a folder for Basin Delineation results: Output/Testing-YYYY-MM-DD-HH-MM-SS/[server]/BasinDelineations
        delineationDirectory = os.path.join(serverFolderDirectory, r'BasinDelineations')
        if not os.path.exists(delineationDirectory):
            os.makedirs(delineationDirectory)

        # Create a folder for Basin Characteristics results: Output/Testing-YYYY-MM-DD-HH-MM-SS/[server]/BasinCharacteristics
        basinCharacteristicsDirectory = os.path.join(serverFolderDirectory, r'BasinCharacteristics')
        if not os.path.exists(basinCharacteristicsDirectory):
            os.makedirs(basinCharacteristicsDirectory)

        # Create a folder for Flow Statistics results: Output/Testing-YYYY-MM-DD-HH-MM-SS/[server]/FlowStatistics
        flowStatsDirectory = os.path.join(serverFolderDirectory, r'FlowStatistics')
        if not os.path.exists(flowStatsDirectory):
            os.makedirs(flowStatsDirectory)

    serverStartTime = datetime.now()

    printOut("========== PERFORMING TESTS ON " + server.upper() + " SERVER ==========")



    for site in sites:
        
        coordinates = site['geometry']['coordinates']
        xlocation = coordinates[0]
        ylocation = coordinates[1]
        properties = site['properties']
        siteID = properties['siteid']
        region = properties['state']
        testData = properties['testData']
        basinDelineationSuccess = True

        printOut("*** " + region + " ***")

        # BASIN DELINEATION
        printOut("BASIN DELINEATION:")
        printOut("Running...")

        for attempt in range(10):
            try:
                basinDelineationStartTime = datetime.now()
                delineateWatershedByLocationString = "https://{}.streamstats.usgs.gov/streamstatsservices/watershed.geojson?rcode={}&xlocation={}&ylocation={}&crs=4326&includeparameters=false&includeflowtypes=false&includefeatures=true&simplify=false".format(server, region, xlocation, ylocation)
                response = requests.get(delineateWatershedByLocationString)
                workspaceID = json.loads(response.content)['workspaceID']
                coordinates = json.loads(response.content)['featurecollection'][1]['feature']['features'][0]["geometry"]['coordinates']
                
                # TODO change this from "test" delineation directory (and similar below)
                siteDelineationFileName = os.path.join(delineationDirectory, region + ".txt")
                siteDelineationFile = open(siteDelineationFileName, "w")
                siteDelineationFile.write(json.dumps(json.loads(response.content)))

                basinDelineationEndTime = datetime.now()
                basinDelineationTimeElapsed = basinDelineationEndTime - basinDelineationStartTime
                printOut("Completed successfully.") # Print the time it took to the console + elapsed time
                printOut("Time elapsed: " + str(basinDelineationTimeElapsed)) # Print the time it took to the console + elapsed time
                # Print the time it took in the output.txt + elapsed time
            except Exception as e:
                printOut("Failed. Retrying...")
                # printOut(e)
            else:
                break
        else:
            printOut("Failed 10 times. Moving on to the next region.")
            basinDelineationSuccess = False
        
        # BASIN CHARACTERISTICS

        if basinDelineationSuccess:
            
            printOut("BASIN CHARACTERISTICS:")
            printOut("Running...")



            for attempt in range(10):
                try:
                    basinCharacteristicsStartTime = datetime.now()
                    computeBasinCharacteristicsString = "https://{}.streamstats.usgs.gov/streamstatsservices/parameters.json?rcode={}&workspaceID={}&includeparameters=true".format(server, region, workspaceID)
                    response = requests.get(computeBasinCharacteristicsString)
                    parameters = json.loads(response.content)['parameters']
                    
                    # printOut(parameters)

                    siteBasinCharcteristicsFileName = os.path.join(basinCharacteristicsDirectory, region + ".txt")
                    siteBasinCharcteristicsFile = open(siteBasinCharcteristicsFileName, "w")
                    # printOut(json.loads(response.content))
                    siteBasinCharcteristicsFile.write(json.dumps(json.loads(response.content)))
                    # printOut(json.dumps(json.loads(response.content)))

                    basinCharacteristicsEndTime = datetime.now()
                    basinCharacteristicsTimeElapsed = basinCharacteristicsEndTime - basinCharacteristicsStartTime
                    # basinCharacteristicsElapsed = basinCharacteristicsTime.strftime("%Y/%m/%d %H:%M:%S")
                    printOut("Completed successfully.")
                    printOut("Time elapsed: " + str(basinCharacteristicsTimeElapsed))
                    # Print the time it took in the output.txt + elapsed time

                    printOut("COMPARING BASIN CHARACTERISTICS TO KNOWN VALUES:")
                    printOut("Running...")

                    # Create a file where basin characteristics comparison will be saved
                    fileName = os.path.join(basinCharacteristicsDirectory, "BasinCharacteristicsComparison.csv")
                    basinCharacteristicsComparisonFile = open(fileName, "w")

                    # Make dictionary of known basin characteristics values
                    knownBasinCharacteristicsDictionary = {}
                    knownBasinCharacteristics = site['properties']['testData']
                    for knownBasinCharacteristic in knownBasinCharacteristics:
                        knownBasinCharacteristicsDictionary[knownBasinCharacteristic["Label"]] = knownBasinCharacteristic["Value"]
                    knownBasinCharacteristicsDictionary["L3_PIEDMNT"] = 50

                    numberBasinCharacteristicsNotEqualToKnownValues = 0
                    for parameter in parameters:
                        try:
                            if knownBasinCharacteristicsDictionary[parameter['code']] != parameter['value']:
                                printOut("Basin characteristic not equal to known value: " + parameter['code'])
                                printOut("Known value = " + str(knownBasinCharacteristicsDictionary[parameter['code']]))
                                printOut("Computed value = " + str(parameter['value']))
                                numberBasinCharacteristicsNotEqualToKnownValues += 1
                        except:
                            printOut("No known value for " + parameter['code'] + ". Computed value cannot be compared.")
                    if numberBasinCharacteristicsNotEqualToKnownValues == 0:
                        printOut("Completed. All computed values were equal to known values.")
                    elif numberBasinCharacteristicsNotEqualToKnownValues == 1:
                        printOut("Completed. 1 value was not equal to known values.")
                    else:
                        printOut("Completed. " + str(numberBasinCharacteristicsNotEqualToKnownValues) + " values were not equal to known values.")

                except Exception as e:
                    printOut("Failed. Retrying...")
                    # printOut(e)
                else:
                    break
            else:
                printOut("Failed 10 times. Moving on to the next region.")
                basinCharateristicsSuccess = False

    serverEndTime = datetime.now()
    serverTimeElapsed = serverEndTime - serverStartTime
    printOut(server.upper() + " server finished testing! Elapsed time for this server: " + str(serverTimeElapsed)) 
    # outputFile.write(server.capitalize() + "server finished testing! Elapsed time for this server: " + str(serverTimeElapsed)) 

overallEndTime = datetime.now()
overallTimeElapsed = overallEndTime - overallStartTime
printOut("Testing complete! Overall elapsed time: " + str(overallTimeElapsed))
consoleOutputFile.close()