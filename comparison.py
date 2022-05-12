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
from tkinter import filedialog
from tkinter import *
import pathlib

# Create Output folder if it doesn't exist
currentDirectory = os.getcwd()
outputDirectory = os.path.join(currentDirectory, r'Output')
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

# Create a folder for this comparison: Output/Comparison-YYYY-MM-DD-HH-MM-SS
overallStartTime = datetime.now()
folderName = "Comparison-" + overallStartTime.strftime("%Y-%m-%d-%H-%M-%S")
dateDirectory = os.path.join(outputDirectory, folderName)
if not os.path.exists(dateDirectory):
    os.makedirs(dateDirectory)
    print("Creating new folder in Output folder: " + folderName)

# Create a file where console output will be saved
fileName = os.path.join(dateDirectory, "ConsoleOutput.txt")
consoleOutputFile = open(fileName, "w")

# Create a summary file to show all comparisons
fileName = os.path.join(dateDirectory, "Comparison.csv")
comparisonSummaryFile = open(fileName, "w", newline='')
comparisonSummaryFileWriter = csv.writer(comparisonSummaryFile)
headerRow = ["Comparison Session", "Testing Session 1", "Testing Session 2", "Server", "File Name", "Task", "Description", "Testing Session 1 Value", "Testing Session 2 Value", "Testing Session 1 value equal to Testing Session 2 value?"]
comparisonSummaryFileWriter.writerow(headerRow)
comparisonSummaryFile.flush()

# Create a summary file to show all differences
fileName = os.path.join(dateDirectory, "ComparisonDifferences.csv")
comparisonDifferencesFile = open(fileName, "w", newline='')
comparisonDifferencesFileWriter = csv.writer(comparisonDifferencesFile)
headerRow = ["Comparison Session", "Testing Session 1", "Testing Session 2", "Server", "File Name", "Task", "Description", "Testing Session 1 Value", "Testing Session 2 Value", "Testing Session 1 value equal to Testing Session 2 value?"]
comparisonDifferencesFileWriter.writerow(headerRow)
comparisonDifferencesFile.flush()

# Create a summary file to show all uncompared values
fileName = os.path.join(dateDirectory, "ComparisonUncompared.csv")
comparisonUncomparedFile = open(fileName, "w", newline='')
comparisonUncomparedFileWriter = csv.writer(comparisonUncomparedFile)
headerRow = ["Comparison Session", "Testing Session 1", "Testing Session 2", "Server", "File Name", "Task", "Description", "Testing Session 1 Value", "Testing Session 2 Value", "Testing Session 1 value equal to Testing Session 2 value?"]
comparisonUncomparedFileWriter.writerow(headerRow)
comparisonUncomparedFile.flush()

# Prompt the user to select the 2 Testing Session Folders (Testing-YYYY-MM-DD-HH-MM-SS) to be compared
root = Tk()
root.withdraw()
testingSession1Directory = filedialog.askdirectory(title="Select Testing Session 1 Folder", initialdir=outputDirectory)
testingSession1Path = pathlib.PurePath(testingSession1Directory)
testingSession1Name = testingSession1Path.name
testingSession2Directory = filedialog.askdirectory(title="Select Testing Session 2 Folder", initialdir=outputDirectory)
testingSession2Path = pathlib.PurePath(testingSession2Directory)
testingSession2Name = testingSession2Path.name

printOut("Comparing these 2 Testing Sessions:")
printOut(testingSession1Name)
printOut(testingSession2Name)

servers = ["TEST", "PRODWEBA", "PRODWEBB"]

for server in servers:

    printOut("========== COMPARING " + server + " RESULTS ==========")

    testingSession1ServerDirectory = os.path.join(testingSession1Path, server)
    testingSession2ServerDirectory = os.path.join(testingSession2Path, server)

    # Compare Basin Delineations
    printOut("BASIN DELINEATION:")
    filesBasinDelineation = []
    testingSession1ServerBasinDelineationDirectory = os.path.join(testingSession1ServerDirectory, "BasinDelineations")
    testingSession2ServerBasinDelineationDirectory = os.path.join(testingSession2ServerDirectory, "BasinDelineations")
    # Check the files from Testing Session 1
    for file in os.listdir(testingSession1ServerBasinDelineationDirectory):
        if file.endswith(".txt"):
            filesBasinDelineation.append(file)
            print("Comparing: " + file)
            basinDelineationServer1FileName = os.path.join(testingSession1ServerBasinDelineationDirectory, file)
            basinDelineationServer1File = open(basinDelineationServer1FileName, "r")
            try:
                basinDelineationServer2FileName = os.path.join(testingSession2ServerBasinDelineationDirectory, file)
                basinDelineationServer2File = open(basinDelineationServer2FileName, "r")
                basinDelineationServer1Coordinates = json.load(basinDelineationServer1File)['featurecollection'][1]['feature']['features'][0]["geometry"]['coordinates']
                basinDelineationServer2Coordinates = json.load(basinDelineationServer2File)['featurecollection'][1]['feature']['features'][0]["geometry"]['coordinates']
                if basinDelineationServer1Coordinates == basinDelineationServer2Coordinates:
                    printOut("Basin Delineations are equal.")
                else:
                    printOut("Basin Delineations are not equal.")
                    dataRow = [folderName, testingSession1Name, testingSession2Name, server, file, "BasinDelineation", "", "See file", "See file", str(False)]
                    comparisonDifferencesFileWriter.writerow(dataRow)
                    comparisonDifferencesFile.flush()
                dataRow = [folderName, testingSession1Name, testingSession2Name, server, file, "BasinDelineation", "", "See file", "See file", str(basinDelineationServer1Coordinates == basinDelineationServer2Coordinates)]
                comparisonSummaryFileWriter.writerow(dataRow)
                comparisonSummaryFile.flush()
            except FileNotFoundError: 
                printOut("Basin Delineation available for only one testing session. Cannot compare.")
                dataRow = [folderName, testingSession1Name, testingSession2Name, server, file, "BasinDelineation", "", "See file", "File not found", str(False)]
                comparisonUncomparedFileWriter.writerow(dataRow)
                comparisonUncomparedFile.flush()
        else:
            continue
    # Check the files from Testing Session 2 that were not in Testing Session 1
    for file in os.listdir(testingSession2ServerBasinDelineationDirectory):
        if file.endswith(".txt"):
            if file not in filesBasinDelineation:
                print("Comparing: " + file)
                printOut("Basin Delineation available for only one testing session. Cannot compare.")
                dataRow = [folderName, testingSession1Name, testingSession2Name, server, file, "BasinDelineation", "", "File not found", "See file", str(False)]
                comparisonUncomparedFileWriter.writerow(dataRow)
                comparisonUncomparedFile.flush()
        else:
            continue




    # Compare Basin Characteristics
    printOut("BASIN CHARACTERISTICS:")
    testingSession1ServerBasinCharacteristicsDirectory = os.path.join(testingSession1ServerDirectory, "BasinCharacteristics")
    testingSession2ServerBasinCharacteristicsDirectory = os.path.join(testingSession2ServerDirectory, "BasinCharacteristics")
    for file in os.listdir(testingSession1ServerBasinCharacteristicsDirectory):
        if file.endswith(".txt"):
            printOut("Comparing: " + file)
        else:
            continue

    # Compare Flow Statistics
    printOut("FLOW STATISTICS:")
    testingSession1ServerFlowStatisticsDirectory = os.path.join(testingSession1ServerDirectory, "FlowStatistics")
    testingSession2ServerFlowStatisticsDirectory = os.path.join(testingSession2ServerDirectory, "FlowStatistics")
    for file in os.listdir(testingSession1ServerFlowStatisticsDirectory):
        if file.endswith(".txt"):
            printOut("Comparing: " + file)
        else:
            continue