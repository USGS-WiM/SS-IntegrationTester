# Print out text string to console and to ConsoleOutput.txt
def printOut(text):
    print(text)
    global consoleOutputFile
    consoleOutputFile.write(text + "\n")
    consoleOutputFile.flush()

from fileinput import filename
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

# Create a file where time elapsed will be saved
fileName = os.path.join(dateDirectory, "TimeElapsed.csv")
timeElapsedFile = open(fileName, "w", newline='')
timeElapsedFileWriter = csv.writer(timeElapsedFile)
headerRow = ["Testing session", "Server", "Region", "SiteID", "Task", "Time elapsed"]
timeElapsedFileWriter.writerow(headerRow)
timeElapsedFile.flush()

# Load the test sites from local files
testSites = open('testSites.geojson')
fakeTestSites = open('fakeTestSites.geojson')
sites = json.load(fakeTestSites)['features']

servers = ["prodweba", "prodwebb"]
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

        # Create a file where basin characteristics comparison will be saved
        fileName = os.path.join(basinCharacteristicsDirectory, "BasinCharacteristicsComparison.csv")
        basinCharacteristicsComparisonFile = open(fileName, "w", newline='')
        basinCharacteristicsComparisonFileWriter = csv.writer(basinCharacteristicsComparisonFile)
        headerRow = ["Region", "SiteID", "WorkspaceID", "Latitude", "Longitude", "Basin Characteristic", "Computed value", "Known value", "Computed Value Equal to Known Value?"]
        basinCharacteristicsComparisonFileWriter.writerow(headerRow)
        basinCharacteristicsComparisonFile.flush()

        # Create a file where computed basin characteristics that are different from known values will be saved
        fileName = os.path.join(basinCharacteristicsDirectory, "BasinCharacteristicsDifferences.csv")
        basinCharacteristicsDifferenceFile = open(fileName, "w", newline='')
        basinCharacteristicsDifferenceFileWriter = csv.writer(basinCharacteristicsDifferenceFile)
        headerRow = ["Region", "SiteID", "WorkspaceID", "Latitude", "Longitude", "Basin Characteristic", "Computed value", "Known value"]
        basinCharacteristicsDifferenceFileWriter.writerow(headerRow)
        basinCharacteristicsDifferenceFile.flush()

        # Create a file where computed basin characteristics that were not compared to known values will be saved
        fileName = os.path.join(basinCharacteristicsDirectory, "BasinCharacteristicsUncompared.csv")
        basinCharacteristicsUncomparedFile = open(fileName, "w", newline='')
        basinCharacteristicsUncomparedFileWriter = csv.writer(basinCharacteristicsUncomparedFile)
        headerRow = ["Region", "SiteID", "WorkspaceID", "Latitude", "Longitude", "Basin Characteristic", "Computed value"]
        basinCharacteristicsUncomparedFileWriter.writerow(headerRow)
        basinCharacteristicsUncomparedFile.flush()

        # Create a folder for Flow Statistics results: Output/Testing-YYYY-MM-DD-HH-MM-SS/[server]/FlowStatistics
        flowStatsDirectory = os.path.join(serverFolderDirectory, r'FlowStatistics')
        if not os.path.exists(flowStatsDirectory):
            os.makedirs(flowStatsDirectory)

    serverStartTime = datetime.now()

    printOut("========== PERFORMING TESTS ON " + server.upper() + " SERVER ==========")

    for site in sites:

        
        siteStartTime = datetime.now()
        
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
                
                siteDelineationFileName = os.path.join(delineationDirectory, region + ".txt")
                siteDelineationFile = open(siteDelineationFileName, "w")
                siteDelineationFile.write(json.dumps(json.loads(response.content)))
                siteDelineationFile.close()

                basinDelineationEndTime = datetime.now()
                basinDelineationTimeElapsed = basinDelineationEndTime - basinDelineationStartTime
                printOut("Completed successfully. Time elapsed: " + str(basinDelineationTimeElapsed)) 
                dataRow = [folderName, server.upper(), region, siteID, "Basin Delineation", basinDelineationTimeElapsed]
                timeElapsedFileWriter.writerow(dataRow)
                timeElapsedFile.flush()

            except Exception as e:
                printOut("Failed. Retrying...")
                print(e)
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

                    # Check to make sure that values were actually returned from the service
                    if 'value' not in parameters[0]:
                        raise Exception
                    
                    siteBasinCharcteristicsFileName = os.path.join(basinCharacteristicsDirectory, region + ".txt")
                    siteBasinCharcteristicsFile = open(siteBasinCharcteristicsFileName, "w")
                    siteBasinCharcteristicsFile.write(json.dumps(json.loads(response.content)))
                    siteBasinCharcteristicsFile.close()

                    basinCharacteristicsEndTime = datetime.now()
                    basinCharacteristicsTimeElapsed = basinCharacteristicsEndTime - basinCharacteristicsStartTime
                    printOut("Completed successfully. Time elapsed: " + str(basinCharacteristicsTimeElapsed)) 
                    dataRow = [folderName, server.upper(), region, siteID, "Basin Characteristics", basinCharacteristicsTimeElapsed]
                    timeElapsedFileWriter.writerow(dataRow)
                    timeElapsedFile.flush()

                    printOut("COMPARING BASIN CHARACTERISTICS TO KNOWN VALUES:")
                    printOut("Running...")

                    # Make dictionary of known basin characteristics values
                    knownBasinCharacteristicsDictionary = {}
                    knownBasinCharacteristics = site['properties']['testData']
                    for knownBasinCharacteristic in knownBasinCharacteristics:
                        knownBasinCharacteristicsDictionary[knownBasinCharacteristic["Label"]] = knownBasinCharacteristic["Value"]

                    numberBasinCharacteristicsNotEqualToKnownValues = 0
                    for parameter in parameters:
                        try:
                            if knownBasinCharacteristicsDictionary[parameter['code']] != parameter['value']:
                                printOut("Basin characteristic not equal to known value: " + parameter['code'])
                                printOut("Known value = " + str(knownBasinCharacteristicsDictionary[parameter['code']]))
                                printOut("Computed value = " + str(parameter['value']))
                                numberBasinCharacteristicsNotEqualToKnownValues += 1
                                dataRow = [region, siteID, workspaceID, ylocation, xlocation, parameter['code'], parameter['value'], knownBasinCharacteristicsDictionary[parameter['code']]]
                                basinCharacteristicsDifferenceFileWriter.writerow(dataRow)
                                basinCharacteristicsDifferenceFile.flush()
                            dataRow = [region, siteID, workspaceID, ylocation, xlocation, parameter['code'], parameter['value'], knownBasinCharacteristicsDictionary[parameter['code']], str(knownBasinCharacteristicsDictionary[parameter['code']] == parameter['value'])]
                            basinCharacteristicsComparisonFileWriter.writerow(dataRow)
                            basinCharacteristicsComparisonFile.flush()
                        except Exception as e:
                            try:
                                printOut("No known value for " + parameter['code'] + ". Computed value cannot be compared.")
                                dataRow = [region, siteID, workspaceID, ylocation, xlocation, parameter['code'], parameter['value']]
                                basinCharacteristicsUncomparedFileWriter.writerow(dataRow)
                                basinCharacteristicsUncomparedFile.flush()
                                dataRow = [region, siteID, workspaceID, ylocation, xlocation, parameter['code'], parameter['value'], "None", "Not applicable"]
                                basinCharacteristicsComparisonFileWriter.writerow(dataRow)
                                basinCharacteristicsComparisonFile.flush()
                            except Exception as e:
                                # print(e)
                                break

                    if numberBasinCharacteristicsNotEqualToKnownValues == 0:
                        printOut("Completed. All computed values were equal to known values.")
                    elif numberBasinCharacteristicsNotEqualToKnownValues == 1:
                        printOut("Completed. 1 value was not equal to known values.")
                    else:
                        printOut("Completed. " + str(numberBasinCharacteristicsNotEqualToKnownValues) + " values were not equal to known values.")

                except Exception as e:
                    printOut("Failed. Retrying...")
                    # print(e)
                else:
                    break
            else:
                printOut("Failed 10 times. Moving on to the next region.")
                basinCharateristicsSuccess = False
        
        siteEndTime = datetime.now()
        siteTimeElapsed = siteEndTime - siteStartTime
        dataRow = [folderName, server.upper(), region, siteID, "", siteTimeElapsed]
        timeElapsedFileWriter.writerow(dataRow)
        timeElapsedFile.flush()

    serverEndTime = datetime.now()
    serverTimeElapsed = serverEndTime - serverStartTime
    printOut(server.upper() + " server finished testing! Elapsed time for this server: " + str(serverTimeElapsed)) 
    dataRow = [folderName, server.upper(), "", "", "", serverTimeElapsed]
    timeElapsedFileWriter.writerow(dataRow)
    timeElapsedFile.flush()

overallEndTime = datetime.now()
overallTimeElapsed = overallEndTime - overallStartTime
printOut("Testing complete! Overall elapsed time: " + str(overallTimeElapsed))
dataRow = [folderName, "", "", "", "", overallTimeElapsed]
timeElapsedFileWriter.writerow(dataRow)
timeElapsedFile.flush()
consoleOutputFile.close()
timeElapsedFile.close()
basinCharacteristicsComparisonFile.close()
basinCharacteristicsDifferenceFile.close()
basinCharacteristicsUncomparedFile.close()