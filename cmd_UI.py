# An object of this type holds the name of a Maya command and a dictionary with all CP objects
#   corresponding to that command

# The constructor will create a file named according to the command and with the suffix, "_call.py".
#   This file defines a single function, call(), to which the object can be passed to invoke the 
#   actual Maya command

class Cmd_UI:

    def __init__(self, commandName, paramList):

        self.commandName = commandName
        self.paramUIs = {}
        for p in paramList:

            self.paramUIs[p.shortName] = p

        self.createCommandCallerFile()

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