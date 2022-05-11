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
import urllib.request

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
headerRow = ["Testing session", "Server", "Region", "SiteID", "WorkspaceID", "Task", "Time elapsed"]
timeElapsedFileWriter.writerow(headerRow)
timeElapsedFile.flush()

# Load the test sites from local files
testSites = open('testSites.geojson') # Real test sites file
fakeTestSites = open('fakeTestSites.geojson') # Fake test sites file used for testing purposes
sites = json.load(fakeTestSites)['features']

servers = ["test", "prodweba", "prodwebb"]
resultsFolders = ["BasinDelineations", "BasinCharacteristics", "FlowStatistics"]

for server in servers:

    # Check the connection and skip if server is down 
    try:
        serverString = "https://{}.streamstats.usgs.gov/ss".format(server)
        urllib.request.urlopen(serverString).getcode()

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
            flowStatisticsDirectory = os.path.join(serverFolderDirectory, r'FlowStatistics')
            if not os.path.exists(flowStatisticsDirectory):
                os.makedirs(flowStatisticsDirectory)

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
            basinCharateristicsSuccess = True
            flowStatisticsSuccess = True

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
                    dataRow = [folderName, server.upper(), region, siteID, workspaceID, "Basin Delineation", basinDelineationTimeElapsed]
                    timeElapsedFileWriter.writerow(dataRow)
                    timeElapsedFile.flush()

                except Exception as e:
                    printOut("Failed. Retrying...")
                    # print(e)
                else:
                    break
            else:
                printOut("Failed 10 times. Moving on to the next site.")
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
                        dataRow = [folderName, server.upper(), region, siteID, workspaceID, "Basin Characteristics", basinCharacteristicsTimeElapsed]
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
                        else:
                            printOut("Completed. Number of Basin Characteristics not equal to known values: " + str(numberBasinCharacteristicsNotEqualToKnownValues))

                    except Exception as e:
                        printOut("Failed. Retrying...")
                        # print(e)
                    else:
                        break
                else:
                    printOut("Failed 10 times. Moving on to the next site.")
                    basinCharateristicsSuccess = False

                # FLOW STATISTICS
                
                if (basinCharateristicsSuccess):
                    
                    printOut("FLOW STATISTICS:")
                    printOut("Running...")

                    for attempt in range(10):
                        try:
                            
                            flowStatisticsStartTime = datetime.now()
                            computeFlowStatisticsString = "https://{}.streamstats.usgs.gov/streamstatsservices/flowstatistics.json?rcode={}&workspaceID={}&includeflowtypes=true".format(server, region, workspaceID)
                            response = requests.get(computeFlowStatisticsString)
                            regressionRegions = json.loads(response.content)[0]['RegressionRegions']

                            # Check to make sure that values were actually returned from the service
                            if 'value' not in parameters[0]:
                                raise Exception

                            siteFlowStatisticsFileName = os.path.join(flowStatisticsDirectory, region + ".txt")
                            siteFlowStatisticsFile = open(siteFlowStatisticsFileName, "w")
                            siteFlowStatisticsFile.write(json.dumps(json.loads(response.content)))
                            siteFlowStatisticsFile.close()

                            
                            flowStatisticsEndTime = datetime.now()
                            flowStatisticsTimeElapsed = flowStatisticsEndTime - flowStatisticsStartTime
                            printOut("Completed successfully. Time elapsed: " + str(flowStatisticsTimeElapsed)) 
                            dataRow = [folderName, server.upper(), region, siteID, workspaceID, "FlowStatistics", flowStatisticsTimeElapsed]
                            timeElapsedFileWriter.writerow(dataRow)
                            timeElapsedFile.flush()
                            
                        except Exception as e:
                            if (response.status_code == 500):
                                printOut("Flow Statistics not available for this site. Moving on to the next site.")
                                flowStatisticsSuccess = False
                                break
                            else:
                                printOut("Failed. Retrying...")
                                # print(e)
                        else:
                            break
                    else: 
                        printOut("Failed 10 times. Moving on to the next site.")
                        flowStatisticsSuccess = False

            
            siteEndTime = datetime.now()
            siteTimeElapsed = siteEndTime - siteStartTime
            dataRow = [folderName, server.upper(), region, siteID, workspaceID, "", siteTimeElapsed]
            timeElapsedFileWriter.writerow(dataRow)
            timeElapsedFile.flush()

        serverEndTime = datetime.now()
        serverTimeElapsed = serverEndTime - serverStartTime
        printOut(server.upper() + " server finished testing! Elapsed time for this server: " + str(serverTimeElapsed)) 
        dataRow = [folderName, server.upper(), "", "", "", "", serverTimeElapsed]
        timeElapsedFileWriter.writerow(dataRow)
        timeElapsedFile.flush()

    except Exception as e:
        # print(e)
        print(server.upper() + " server is down. Moving on to next server.")

## Compare Test to ProdWebA and ProdWebB

# All comparision results files will go in Output/Testing-YYYY-MM-DD-HH-MM-SS/Comparision directory
comparisonDirectory = os.path.join(dateDirectory, "Comparison")
if not os.path.exists(comparisonDirectory):
    os.makedirs(comparisonDirectory)

# Create a summary file to summarize differences 
fileName = os.path.join(comparisonDirectory, "DifferencesSummary.csv")
comparisonSummaryFile = open(fileName, "w", newline='')
comparisonSummaryFileWriter = csv.writer(comparisonSummaryFile)
headerRow = ["Testing session", "Server 1", "Server 2", "Region", "SiteID", "Task", "Description", "Server 1 Value", "Server 2 Value"]
comparisonSummaryFileWriter.writerow(headerRow)
comparisonSummaryFile.flush()

productionServers = ["PRODWEBA", "PRODWEBB"]

# Compare Test to ProdWebA or ProdWebB
for productionServer in productionServers:

    # Results files for this server comparision will go in Output/Testing-YYYY-MM-DD-HH-MM-SS/Comparision/Comparison-TEST-[PRODWEBA OR PRODWEBB] directory
    comparisonTestProdDirectory = os.path.join(comparisonDirectory, "Comparison-TEST-" + productionServer)
    if not os.path.exists(comparisonTestProdDirectory):
        os.makedirs(comparisonTestProdDirectory)

    testDirectory = os.path.join(dateDirectory, "TEST")
    prodDirectory = os.path.join(dateDirectory, productionServer)

    ## Create files where comparisons will be saved
    # This file will include all comparisions
    fileName = os.path.join(comparisonTestProdDirectory, "Comparison-TEST-" + productionServer + ".csv")
    comparisonTestProdFile = open(fileName, "w", newline='')
    comparisonTestProdFileWriter = csv.writer(comparisonTestProdFile)
    headerRow = ["Testing session", "Server 1", "Server 2", "Region", "SiteID", "Task", "Description", "Server 1 Value", "Server 2 Value", "Server 1 value equal to Server 2 value?"]
    comparisonTestProdFileWriter.writerow(headerRow)
    comparisonTestProdFile.flush()

    # This file will include only results that were different between the 2 servers
    fileName = os.path.join(comparisonTestProdDirectory, "Comparison-TEST-" + productionServer + "-Differences.csv")
    comparisonTestProdDifferencesFile = open(fileName, "w", newline='')
    comparisonTestProdDifferencesFileWriter = csv.writer(comparisonTestProdDifferencesFile)
    headerRow = ["Testing session", "Server 1", "Server 2", "Region", "SiteID", "Task", "Description", "Server 1 Value", "Server 2 Value"]
    comparisonTestProdDifferencesFileWriter.writerow(headerRow)
    comparisonTestProdDifferencesFile.flush()

    # This fill will include only results that were not able to be compared because they were unavailable on one server
    fileName = os.path.join(comparisonTestProdDirectory, "Comparison-TEST-" + productionServer + "-Uncompared.csv")
    comparisonTestProdUncomparedFile = open(fileName, "w", newline='')
    comparisonTestProdUncomparedFileWriter = csv.writer(comparisonTestProdUncomparedFile)
    headerRow = ["Testing session", "Server 1", "Server 2", "Region", "SiteID", "Task", "Description", "Server 1 Value", "Server 2 Value"]
    comparisonTestProdUncomparedFileWriter.writerow(headerRow)
    comparisonTestProdUncomparedFile.flush()

    printOut("========== COMPARING TEST AND " + productionServer + " RESULTS ==========")

    for site in sites:

        properties = site['properties']
        siteID = properties['siteid']
        region = properties['state']

        printOut("*** " + region + " ***")

        # Compare Basin Delineation results
        printOut("BASIN DELINEATION:")

        try:
            testBasinDelineationDirectory = os.path.join(testDirectory, "BasinDelineations")
            testBasinDelineationsFileName = os.path.join(testBasinDelineationDirectory, region + ".txt")
            testBasinDelineationsFileNotFound = False        
            testBasinDelineationsFile = open(testBasinDelineationsFileName, "r")
        except FileNotFoundError:
            testBasinDelineationsFileNotFound = True

        try:
            prodBasinDelineationDirectory = os.path.join(prodDirectory, "BasinDelineations")
            prodBasinDelineationsFileName = os.path.join(prodBasinDelineationDirectory, region + ".txt")
            prodBasinDelineationsFileNotFound = False
            prodBasinDelineationsFile = open(prodBasinDelineationsFileName, "r")
        except FileNotFoundError:
            prodBasinDelineationsFileNotFound = True
        
        if (testBasinDelineationsFileNotFound is False and prodBasinDelineationsFileNotFound is False):
            testBasinDelineationCoordinates = json.load(testBasinDelineationsFile)['featurecollection'][1]['feature']['features'][0]["geometry"]['coordinates']
            prodBasinDelineationCoordinates = json.load(prodBasinDelineationsFile)['featurecollection'][1]['feature']['features'][0]["geometry"]['coordinates']
            if testBasinDelineationCoordinates == prodBasinDelineationCoordinates:
                printOut("Basin Delineations are equal.")
            else: 
                printOut("Basin Delineations are not equal.")
                dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinDelineation", "", "See file", "See file"]
                comparisonTestProdDifferencesFileWriter.writerow(dataRow)
                comparisonTestProdDifferencesFile.flush()
                comparisonSummaryFileWriter.writerow(dataRow)
                comparisonSummaryFile.flush()
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinDelineation", "", "See file", "See file", str(testBasinDelineationCoordinates == prodBasinDelineationCoordinates)]
            comparisonTestProdFileWriter.writerow(dataRow)
            comparisonTestProdFile.flush()
        elif (testBasinDelineationsFileNotFound is True and prodBasinDelineationsFileNotFound is True):
            printOut("Basin Delineations are equal.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinDelineation", "", "See file", "See file", str(True)]
            comparisonTestProdFileWriter.writerow(dataRow)
            comparisonTestProdFile.flush()
        else:
            printOut("Basin Delineations available for only one server. Cannot compare.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinDelineation", "", "File not found" if testBasinDelineationsFileNotFound else "See file", "File not found" if prodBasinDelineationsFileNotFound else "See file", "Not applicable"]
            comparisonTestProdFileWriter.writerow(dataRow)
            comparisonTestProdFile.flush()
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinDelineation", "", "File not found" if testBasinDelineationsFileNotFound else "See file", "File not found" if prodBasinDelineationsFileNotFound else "See file"]
            comparisonTestProdUncomparedFileWriter.writerow(dataRow)
            comparisonTestProdUncomparedFile.flush()
            comparisonSummaryFileWriter.writerow(dataRow)
            comparisonSummaryFile.flush()

        # Compare Basin Characteristics results
        printOut("BASIN CHARACTERISTICS:")
        numberBasinCharacteristicsNotEqual = 0

        try:
            testBasinCharacteristicsDirectory = os.path.join(testDirectory, "BasinCharacteristics")
            testBasinCharacteristicsFileName = os.path.join(testBasinCharacteristicsDirectory, region + ".txt")
            testBasinCharacteristicsFileNotFound = False
            testBasinCharacteristicsFile = open(testBasinCharacteristicsFileName, "r")
        except FileNotFoundError:
            testBasinCharacteristicsFileNotFound = True

        try:
            prodBasinCharacteristicsDirectory = os.path.join(prodDirectory, "BasinCharacteristics")
            prodBasinCharacteristicsFileName = os.path.join(prodBasinCharacteristicsDirectory, region + ".txt")
            prodBasinCharacteristicsFileNotFound = False
            prodBasinCharacteristicsFile = open(prodBasinCharacteristicsFileName, "r")
        except FileNotFoundError:
            prodBasinCharacteristicsFileNotFound = True
        
        if (testBasinCharacteristicsFileNotFound is False and prodBasinCharacteristicsFileNotFound is False):
            # Compare the files
            testParameters = json.load(testBasinCharacteristicsFile)['parameters']
            testDictionary = {}
            for testParameter in testParameters:
                testDictionary[testParameter['code']] = testParameter['value']
            prodParameters = json.load(prodBasinCharacteristicsFile)['parameters']
            for prodParameter in prodParameters:
                if testDictionary[prodParameter['code']] != prodParameter['value']:
                    printOut("Basin Characteristic not equal: " + prodParameter['code'])
                    printOut("TEST value = " + str(testDictionary[prodParameter['code']]))
                    printOut(productionServer + " value = " + str(prodParameter['value']))
                    numberBasinCharacteristicsNotEqual+= 1
                    dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinCharacteristics", prodParameter['code'], str(testDictionary[prodParameter['code']]), str(prodParameter['value'])]
                    comparisonTestProdDifferencesFileWriter.writerow(dataRow)
                    comparisonTestProdDifferencesFile.flush()
                    comparisonSummaryFileWriter.writerow(dataRow)
                    comparisonSummaryFile.flush()
                dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinCharacteristics", prodParameter['code'], str(testDictionary[prodParameter['code']]), str(prodParameter['value']), str(testDictionary[prodParameter['code']] == prodParameter['value'])]
                comparisonTestProdFileWriter.writerow(dataRow)
                comparisonTestProdFile.flush()
            if numberBasinCharacteristicsNotEqual > 0:
                printOut("Number of Basin Characteristics not equal between servers: " + str(numberBasinCharacteristicsNotEqual))
            else:
                printOut("All Basin Characteristics are equal.")
        elif (testBasinCharacteristicsFileNotFound is True and prodBasinCharacteristicsFileNotFound is True):
            printOut("All Basin Characteristics are equal.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinCharacteristics", "", "File not found", "File not found"]
            comparisonTestProdFileWriter.writerow(dataRow)
            comparisonTestProdFile.flush()
        else:
            printOut("Basin Characteristics available for only one server. Cannot compare.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "BasinCharacteristics", "", "File not found" if testBasinCharacteristicsFileNotFound else "See file", "File not found" if prodBasinCharacteristicsFileNotFound else "See file"]
            comparisonTestProdUncomparedFileWriter.writerow(dataRow)
            comparisonTestProdUncomparedFile.flush()
            comparisonSummaryFileWriter.writerow(dataRow)
            comparisonSummaryFile.flush()


        # Compare Flow Statistics results
        printOut("FLOW STATISTICS:")
        numberFlowStatisticsNotEqual = 0

        try:
            testFlowStatisticsDirectory = os.path.join(testDirectory, "FlowStatistics")
            testFlowStatisticsFileName = os.path.join(testFlowStatisticsDirectory, region + ".txt")
            testFlowStatisticsFileNotFound = False
            testFlowStatisticsFile = open(testFlowStatisticsFileName, "r")
        except FileNotFoundError:
            testFlowStatisticsFileNotFound = True

        try:
            prodFlowStatisticsDirectory = os.path.join(prodDirectory, "FlowStatistics")
            prodFlowStatisticsFileName = os.path.join(prodFlowStatisticsDirectory, region + ".txt")
            prodFlowStatisticsFileNotFound = False
            prodFlowStatisticsFile = open(prodFlowStatisticsFileName, "r")
        except FileNotFoundError:
            prodFlowStatisticsFileNotFound = True
        
        if (testFlowStatisticsFileNotFound is False and prodFlowStatisticsFileNotFound is False):
            # Compare the files
            testStatisticGroups = json.load(testFlowStatisticsFile)
            testDictionary = {}
            for testStatisticGroup in testStatisticGroups:
                testDictionary[testStatisticGroup['StatisticGroupID']] = {}
                for testRegressionRegion in testStatisticGroup['RegressionRegions']:
                    testDictionary[testStatisticGroup['StatisticGroupID']][testRegressionRegion['Code']] = {}
                    for testResult in testRegressionRegion["Results"]:
                        testDictionary[testStatisticGroup['StatisticGroupID']][testRegressionRegion['Code']][testResult["code"]] = testResult["Value"]

            prodStatisticGroups = json.load(prodFlowStatisticsFile)
            for prodStatisticGroup in prodStatisticGroups:
                for prodRegressionRegion in prodStatisticGroup['RegressionRegions']:
                    for prodResult in prodRegressionRegion["Results"]:
                        if testDictionary[prodStatisticGroup['StatisticGroupID']][prodRegressionRegion['Code']][prodResult["code"]] != prodResult["Value"]:
                            numberFlowStatisticsNotEqual += 1
                            dataRow = [folderName, "TEST", productionServer, region, siteID, "FlowStatistics", prodResult["code"], str(testDictionary[prodStatisticGroup['StatisticGroupID']][prodRegressionRegion['Code']][prodResult["code"]]), str(prodResult["Value"])]
                            comparisonTestProdDifferencesFileWriter.writerow(dataRow)
                            comparisonTestProdDifferencesFile.flush()
                            comparisonSummaryFileWriter.writerow(dataRow)
                            comparisonSummaryFile.flush()
                        dataRow = [folderName, "TEST", productionServer, region, siteID, "FlowStatistics", prodResult["code"], str(testDictionary[prodStatisticGroup['StatisticGroupID']][prodRegressionRegion['Code']][prodResult["code"]]), str(prodResult["Value"]), str(testDictionary[prodStatisticGroup['StatisticGroupID']][prodRegressionRegion['Code']][prodResult["code"]] == prodResult["Value"])]
                        comparisonTestProdFileWriter.writerow(dataRow)
                        comparisonTestProdFile.flush()
            if numberFlowStatisticsNotEqual > 0:
                printOut("Number of Flow Statistics not equal: " + str(numberFlowStatisticsNotEqual))
            else:
                printOut("All Flow Statistics are equal.")
        elif (testFlowStatisticsFileNotFound is True and prodFlowStatisticsFileNotFound is True):
            printOut("Flow Statistics are equal.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "FlowStatistics", "", "File not found", "File not found", str(True)]
            comparisonTestProdFileWriter.writerow(dataRow)
            comparisonTestProdFile.flush()
        else:
            printOut("Flow Statistics available for only one server. Cannot compare.")
            dataRow = [folderName, "TEST", productionServer, region, siteID, "FlowStatistics", "", "File not found" if testFlowStatisticsFileNotFound else "See file", "File not found" if prodFlowStatisticsFileNotFound else "See file"]
            comparisonTestProdUncomparedFileWriter.writerow(dataRow)
            comparisonTestProdUncomparedFile.flush()
            comparisonSummaryFileWriter.writerow(dataRow)
            comparisonSummaryFile.flush()

overallEndTime = datetime.now()
overallTimeElapsed = overallEndTime - overallStartTime
printOut("Testing complete! Overall elapsed time: " + str(overallTimeElapsed))
dataRow = [folderName, "", "", "", "", "", overallTimeElapsed]
timeElapsedFileWriter.writerow(dataRow)
timeElapsedFile.flush()
consoleOutputFile.close()
timeElapsedFile.close()
basinCharacteristicsComparisonFile.close()
basinCharacteristicsDifferenceFile.close()
basinCharacteristicsUncomparedFile.close()