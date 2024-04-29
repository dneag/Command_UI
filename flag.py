
import maya.cmds as cmds
import copy

# These classes bind a Maya command's parameter's 'short name' to one or more associated GUI elements
# The purpose is to simplify saving and loading of GUI's associated with commands with lots of parameters,
#   as well as the calls to those commands

# These are the middle tier in a set of wrappers designed for this purpose.
# The lowest, those defined in widgetWrappers.py, are passed to their constructors, while
#   these are passed to MayaCommandUI objects' constructors

class Flag:

    def __init__(self, shortName):

        self.shortName = shortName
    
    def writeSettings(self, file):

        pass

    def loadSettings(self, file):

        pass

class FlagSingle(Flag):

    def __init__(self, shortName, widget):
        
        Flag.__init__(self, shortName)
        self.widget = widget

    def createUI(self, val=None):

        return self.widget.create(val)

    def getParamVal(self, *_):

        return self.widget.getVal()
    
    def enable(self, enabled):

        self.widget.enable(enabled)

    def writeSettings(self, file):

        self.widget.writeVal(file, self.shortName)

    def loadSettings(self, file):

        self.widget.loadVal(file, self.shortName)

class FlagMulti(Flag):

    def __init__(self, shortName, baseWidget):
        
        Flag.__init__(self, shortName)
        self.baseWidget = baseWidget
        self.widgets = []

    def createUI(self, val=None):

        self.widgets.append(copy.deepcopy(self.baseWidget))

        return self.widgets[-1].create(val)

    def getParamVal(self, *_):

        value = []
        for widget in self.widgets:

            value.append(widget.getVal())

        return value

    def getWidget(self, index):

        return self.widgets[index]
    
    def enable(self, index, enabled):

        self.widgets[index].enable(enabled)

    def writeSettings(self, file):

        for i in range(len(self.widgets)):

            self.widgets[i].writeVal(file, self.shortName + str(i))

    def loadSettings(self, file):

        for i in range(len(self.widgets)):

            self.widgets[i].loadVal(file, self.shortName + str(i))

# Need to override getParamVal() for gradients because there is a discrepancy between a gradient's 
#   stored settings value and its command parameter value, unlike other widgets
class FlagMultiGradi(FlagMulti):

    def __init__(self, shortName, baseWidget, valuesPerGradient):
        
        FlagMulti.__init__(self, shortName, baseWidget)

        self.valuesPerGradient = valuesPerGradient

    def getParamVal(self, *_):

        increment = 1. / self.valuesPerGradient
        valuesAsStrings = []

        for gradient in self.widgets:

            valuesAsStrings.append("")

            xValue = 0.0
            while xValue <= 1.:
                valuesAsStrings[-1] += (str(cmds.gradientControlNoAttr(gradient.uiID, q=True, vap=xValue))) + ","
                xValue += increment
        
        return valuesAsStrings if (len(valuesAsStrings) > 1) else valuesAsStrings[0]
    
# Allow adding a flag with no widget or values to save / load
class FlagMulti_NoWidget(Flag):

    def __init__(self, shortName):
        
        Flag.__init__(self, shortName)
        self.paramVal = None

    def setParamVal(self, val):

        self.paramVal = val
        
    def getParamVal(self, *_):

        return self.paramVal
    