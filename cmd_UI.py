import maya.cmds as cmds
from functools import partial
import os
import time

# An object of this type holds the name of a Maya command and a dictionary with all CP objects
#   corresponding to that command

# The constructor will create a file to call the actual Maya command

class Cmd_UI:

    def __init__(self, commandName, settingsPath, paramList):

        self.commandName = commandName
        self.settingsPath = settingsPath if settingsPath.endswith("/") else settingsPath + "/"
        self.presetsMenu = None
        self.currentPreset = None

        self.paramUIs = {}
        for p in paramList:

            self.paramUIs[p.shortName] = p

        self.createCommandCallerFile()

    # Creates a file named according to the command and with the suffix, "_call.py".
    # This file defines a single function, call(), to which a Cmd_UI object can be passed to invoke the 
    #   actual Maya command.
    # Import this file into any code needing to call the command.
    def createCommandCallerFile(self, *_):

        commandCallFile = open("C:/Users/13308/Documents/maya/scripts/" + self.commandName + "_call.py","w")
        commandCallFile.write("import maya.cmds as cmds\n")
        commandCallFile.write("def call(c):\n")
        commandCallFile.write("\tif c.commandName != \"" + self.commandName + "\":\n")
        commandCallFile.write("\t\tprint(\"Error: command passed to call() does not match command in call file\")\n")
        commandCallFile.write("\tvalues=[]\n")
        commandCallFile.write("\tfor p in c.paramUIs:\n")
        commandCallFile.write("\t\tvalues.append(c.paramUIs[p].getParamVal())\n")
        commandCallFile.write("\tprint(\"Calling " + self.commandName + "()\")\n")
        commandCallFile.write("\tcmds." + self.commandName + "(\n")
        valueIndex = 0
        for key in self.paramUIs:

            commandCallFile.write("\t\t" + self.paramUIs[key].shortName + "=values[" + str(valueIndex) + "],\n")
            valueIndex += 1

        commandCallFile.write(")\n")
        commandCallFile.close()

    # This popupMenu will occupy the space of the GUI component created just before it
    # The doSomething function will be triggered any time a new preset is selected
    def makePresetsPopupMenu(self, doSomething=None):

        self.presetsMenu = cmds.popupMenu(button=1) # button=1 means left mouse will open popup
        for fileName in os.listdir(self.settingsPath):
            if fileName.endswith(".txt"):
                cmds.menuItem(fileName, l=fileName,command=partial(self.loadSettings, fileName, doSomething))

    # Called when a menuItem is selected from the presetsMenu
    def loadSettings(self, presetFileName, doSomething=None, someBool=False):

        settingsFO = open(self.settingsPath + presetFileName,"r")

        for key in self.paramUIs:

            self.paramUIs[key].loadSettings(settingsFO)

        print("finished loading " + presetFileName + " preset")
        settingsFO.close()

        self.currentPreset = presetFileName
        
        if doSomething != None:
            doSomething()

    def saveSettings(self, presetFileName):

        if(presetFileName == ""):
            print("you must enter a name for this preset before you can save it")
            return None

        presetFileName = presetFileName if presetFileName.endswith(".txt") else presetFileName + ".txt"
        presetFileName.replace(" ", "_")

        nameTaken = self.checkIfNameTaken(presetFileName)

        overWriteWindowName = "OverwriteWindow" + str(round(time.clock()))

        if (nameTaken):

            self.createOverWriteFileWindow(overWriteWindowName, presetFileName)

        else:

            settingsFO = open(self.settingsPath + presetFileName,"w")

            for key in self.paramUIs:
                self.paramUIs[key].writeSettings(settingsFO)

            cmds.menuItem(presetFileName, l=presetFileName, p=self.presetsMenu,
                command = partial(self.loadSettings, presetFileName))

            print(presetFileName + " preset saved")

    def checkIfNameTaken(self, presetFileName):

        for presetFile in os.listdir(self.settingsPath):
            if (presetFile == presetFileName):
                return True

        return False

    def createOverWriteFileWindow(self, windowName, presetFileName):

        if(cmds.window(windowName, exists=True)):
            cmds.deleteUI(windowName)

        windowTitle = "Overwrite " + presetFileName + " Settings File"
        print("Making overWrite window with name: ", windowName)
        cmds.window(windowName, title=windowTitle, rtf=True, s=False)
        cmds.columnLayout(co=["both", 10], rs=10)
        cmds.columnLayout()
        cmds.text(l="A settings file with this name already exists.")
        cmds.text(l="       Would you like to replace it?")
        cmds.setParent("..")
        cmds.rowColumnLayout(nc=2,co=[1,"left",74], ro=[1,"bottom",10])
        cmds.button(l="yes",w=40,command=partial(self.overwriteSettings, windowName, presetFileName, True))
        cmds.button(l="no",w=40,command=partial(self.overwriteSettings, windowName, presetFileName, False))
        cmds.showWindow()

    def overwriteSettings(self, windowName, presetFileName, overWrite, someBool):

        if overWrite:

            os.remove(self.settingsPath + presetFileName)
            print("Attempting to deleteUI with name: ", presetFileName)

            # Maya changes dots to underscores in its objects' names, so we must do the same to find them
            cmds.deleteUI(presetFileName.replace(".", "_"))

            self.saveSettings(presetFileName)
        
        cmds.deleteUI(windowName)