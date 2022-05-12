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

# Create a summary file to summarize differences 
fileName = os.path.join(dateDirectory, "DifferencesSummary.csv")
comparisonSummaryFile = open(fileName, "w", newline='')
comparisonSummaryFileWriter = csv.writer(comparisonSummaryFile)
headerRow = ["Testing Session 1", "Testing Session 2", "Server", "Region", "SiteID", "Task", "Description", "Testing Session 1 Value", "Testing Session 2 Value"]
comparisonSummaryFileWriter.writerow(headerRow)
comparisonSummaryFile.flush()

# Prompt the user to select the 2 Testing Session Folders (Testing-YYYY-MM-DD-HH-MM-SS) to be compared
root = Tk()
root.withdraw()
testingSession1Directory = filedialog.askdirectory(title="Select Testing Session 1 Folder", initialdir=outputDirectory)
testingSession1Path = pathlib.PurePath(testingSession1Directory)
testingSession2Directory = filedialog.askdirectory(title="Select Testing Session 2 Folder", initialdir=outputDirectory)
testingSession2Path = pathlib.PurePath(testingSession2Directory)

printOut("Comparing these 2 Testing Sessions:")
printOut(testingSession1Path.name)
printOut(testingSession2Path.name)

servers = ["TEST", "PRODWEBA", "PRODWEBB"]


