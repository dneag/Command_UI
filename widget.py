import maya.cmds as cmds
import time, copy

class Widget:
    
    def __init__(self, *_):

        pass

    def writeVal(self, file, settingName):

        file.write(str(self.getVal()) + "?" + settingName + "?\n")

    def loadVal(self, file, settingName):

        line = file.readline().split("?")
        if line[1] != settingName: print("WARNING:  WRONG VALUE READ - " + line[1])
        self.setVal(line[0])

    def initValIsGood(self, initVal, type):

        if type == "int":
            if isinstance(initVal, int):
                pass
            else:
                return False
        elif type == "float":
            if isinstance(initVal, float):
                pass
            else:
                return False
        else:
            return False

        if initVal <= self.min: return False
        elif initVal >= self.max: return False
        
        return True

class IntFld(Widget):

    def __init__(self, min, max, step):

        self.min = min
        self.max = max
        self.step = step

    def create(self, initVal):

        if not self.initValIsGood(initVal, "int"): initVal = self.min

        self.uiID = cmds.intField(v=initVal,min=self.min,max=self.max,s=self.step)

    def getVal(self, *_):
       
        return cmds.intField(self.uiID, q=True, v=True)

    def setVal(self, newVal):

        cmds.intField(self.uiID, e=True, v=int(newVal))
    
    def enable(self, enabled):

        cmds.intField(self.uiID, e=True, en=enabled)

class FloatFld(Widget):

    def __init__(self, min, max, step, precision, changeCommand = None):
        
        self.min = min
        self.max = max
        self.step = step
        self.precision = precision
        self.changeCommand = changeCommand

    def create(self, initVal):

        if not self.initValIsGood(initVal, "float"): initVal = self.min

        if (self.changeCommand):
            self.uiID = cmds.floatField(v=initVal,min=self.min,max=self.max,s=self.step,pre=self.precision,cc=self.changeCommand)
        else:
            self.uiID = cmds.floatField(v=initVal,min=self.min,max=self.max,s=self.step,pre=self.precision)

    def getVal(self, *_):
       
        return cmds.floatField(self.uiID, q=True, v=True)

    def setVal(self, newVal):

        cmds.floatField(self.uiID, e=True, v=float(newVal))
    
    def enable(self, enabled):

        cmds.floatField(self.uiID, e=True, en=enabled)

class TextFld(Widget):

    def __init__(self, *_):
        
        pass

    def create(self, *_):

        self.uiID = cmds.textField()

    def getVal(self, *_):
       
        return cmds.textField(self.uiID, q=True, v=True)

    def setVal(self, newText):

        cmds.textField(self.uiID, e=True, v=newText)

    def enable(self, enabled):

        cmds.floatField(self.uiID, e=True, en=enabled)

class CheckBox(Widget):

    def __init__(self, label):
        
        self.label = label

    def create(self, *_):

        self.uiID = cmds.checkBox(l=self.label,v=0)

    def getVal(self, *_):
       
        value = cmds.checkBox(self.uiID, q=True, v=True)
        return 1 if value else 0

    def setVal(self, newVal):

        cmds.checkBox(self.uiID, e=True, v=int(newVal))
    
    def enable(self, enabled):

        cmds.checkBox(self.uiID, e=True, en=enabled)

class IntSliderFld(Widget):

    def __init__(self, label, min, max, columnWidths):
        
        self.label = label
        self.min = min
        self.max = max
        self.columnWidths = columnWidths

    def create(self, *_):

        self.uiID = cmds.intSliderGrp(v=self.min,min=self.min,max=self.max,f=True,l=self.label,cw3=self.columnWidths)

    def getVal(self, *_):
        
        return cmds.intSliderGrp(self.uiID, q=True, v=True)

    def setVal(self, newVal):

        cmds.intSliderGrp(self.uiID, e=True, v=int(newVal))

class Gradient(Widget):

    def __init__(self, height, width):

        self.height = height
        self.width = width

    def create(self, *_):

        self.uiID = cmds.gradientControlNoAttr(h=self.height, w=self.width, cc=self.printVals)
        self.setVal('.5,0.,3')

    # Return value is a single string.  It is a concatenation of all its optionvar point values
    def getVal(self, *_):

        return cmds.gradientControlNoAttr(self.uiID, q=True, asString=True)

    # values for an optionVar are strings indicating a list indicating attributes of a point on the gradient
    # First is the y location, then x, then the type of curve, i.e. '.5, .7, 3'
    def setVal(self, optionVarValueAsString):

        # First, parse the single string into a list of valid optionVar string values
        values = optionVarValueAsString.split(",")
        ovStringValues = []
        for i in range(len(values)):

            if i%3 == 0: ovStringValues.append("")
            if i%3 != 2: ovStringValues[-1] += values[i] + ","
            else: ovStringValues[-1] += values[i]

        # setting a gradient's value requires a new, uniquely named optionVar
        ovName = "gradientOptionVar" + str(round(time.clock(), 4))

        # the first optionVar call creates the curve/line on the gradient
        # if one already exists with this name, it is replaced
        cmds.optionVar(stringValue=[ovName, ovStringValues[0]])

        # further optionVar calls append more points to the gradient using the stringValueAppend parameter
        for value in ovStringValues[1:]:
            cmds.optionVar(stringValueAppend=[ovName, value])
            
        cmds.gradientControlNoAttr(self.uiID, e=True, optionVar=ovName)

    def printVals(self, pointValues):

        print(pointValues)

# Group classes behave like single widgets, but are actually groups of widgets.
# They can be used for the widget parameter for FlagSingle and FlagMulti.
# By default their getVal() returns a list of all the widgets' values.  If the paramType is specified
#   as 'string', it will return a single string containing each widget value separated by commas
# Note that createUI() calls on flag objects with Grps will create multiple widgets at once, so
#   the calling code must provide the appropriate layout to account for this.
class EmptyGrp:

    def __init__(self, paramType="list"):

        self.widgets = []
        self.paramType = paramType

    def nextWidget(self, newWidget, initVal=None):

        newWidget.create(initVal)
        return newWidget

    def getVal(self, *_):

        if self.paramType == "list":

            value = []
            for widget in self.widgets:
                value.append(widget.getVal())

            return value
        
        elif self.paramType == "string":

            value = "" 
            for widget in self.widgets:
                value += str(widget.getVal()) + ','

            return value

    def writeVal(self, file, settingName):

        for i in range(len(self.widgets)):
            self.widgets[i].writeVal(file, settingName + str(i))

    def loadVal(self, file, settingName):

        for i in range(len(self.widgets)):

            self.widgets[i].loadVal(file, settingName + str(i))

            if type(self.widgets[i]) is FloatFld:

                if (self.widgets[i].changeCommand is not None):

                    self.widgets[i].changeCommand()

class EquiGrp(EmptyGrp):

    def __init__(self, baseWidget, widgetsPerGrp, paramType="list"):

        EmptyGrp.__init__(self, paramType)
        self.baseWidget = baseWidget
        self.widgetsPerGrp = widgetsPerGrp

    def create(self, initValues):

        if isinstance(initValues, list) and len(initValues) == self.widgetsPerGrp:
            
            for i in range(self.widgetsPerGrp):
                self.widgets.append(self.nextWidget(copy.deepcopy(self.baseWidget), initValues[i]))

        else:

            for i in range(self.widgetsPerGrp):
                self.widgets.append(self.nextWidget(copy.deepcopy(self.baseWidget)))

# Contains method for creating a checkbox widget.  Assumes this is always the first widget in the group
class CheckBoxGrp(EmptyGrp):

    def __init__(self, cbLabel, paramType="list"):

        EmptyGrp.__init__(self, paramType)
        self.cbLabel = cbLabel

    def nextCheckBox(self, *_):

        nextCheckBox = CheckBox(self.cbLabel)
        nextCheckBox.uiID = cmds.checkBox(l=self.cbLabel,v=0,cc=self.handleCheckBox)
        return nextCheckBox

    def handleCheckBox(self, cbValue):

        for widget in self.widgets[1:]:
            widget.enable(cbValue)

    def loadVal(self, file, settingName):

        super().loadVal(file, settingName)
        cbValue = self.widgets[0].getVal()

        for widget in self.widgets[1:]:
            widget.enable(cbValue)
