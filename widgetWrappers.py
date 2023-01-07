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

class IntFld(Widget):

    def __init__(self, min, max, step):

        self.min = min
        self.max = max
        self.step = step

    def create(self, *_):

        self.uiID = cmds.intField(v=self.min,min=self.min,max=self.max,s=self.step)

    def getVal(self, *_):
       
        return cmds.intField(self.uiID, q=True, v=True)

    def setVal(self, newVal):

        cmds.intField(self.uiID, e=True, v=int(newVal))
    
    def enable(self, enabled):

        cmds.intField(self.uiID, e=True, en=enabled)

class FloatFld(Widget):

    def __init__(self, min, max, step, precision):
        
        self.min = min
        self.max = max
        self.step = step
        self.precision = precision

    def create(self, *_):

        self.uiID = cmds.floatField(v=self.min,min=self.min,max=self.max,s=self.step,pre=self.precision)

    def getVal(self, *_):
       
        return cmds.floatField(self.uiID, q=True, v=True)

    def setVal(self, newVal):

        cmds.floatField(self.uiID, e=True, v=float(newVal))
    
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

# Grp classes behave like single widgets, but are actually groups of widgets
# They can be used for the widget parameter for PG_Single and PG_Multi
# Their getVal() returns a single string containing each widget value separated by commas
class EmptyGrp:

    def __init__(self):

        self.widgets = []

    def nextWidget(self, nextWidget):

        nextWidget.create()
        return nextWidget

    def getVal(self, *_):

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

class EquiGrp(EmptyGrp):

    def __init__(self, baseWidget, widgetsPerGrp):

        EmptyGrp.__init__(self)
        self.baseWidget = baseWidget
        self.widgetsPerGrp = widgetsPerGrp

    def create(self, *_):

        for i in range(self.widgetsPerGrp):
            self.widgets.append(self.nextWidget(copy.deepcopy(self.baseWidget)))

# Contains method for creating a checkbox widget.  Assumes this is always the first widget in the group
class CheckBoxGrp(EmptyGrp):

    def __init__(self, cbLabel):

        EmptyGrp.__init__(self)
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

class DroopGrp(CheckBoxGrp):

    def __init__(self, cbLabel):

        CheckBoxGrp.__init__(self, cbLabel)

    def create(self, *_):

        cmds.rowColumnLayout(nc=5,cw=[(1,85),(2,60),(3,35),(4,60),(5,35)], co=[(1,"left",10)])
        self.widgets.append(self.nextCheckBox())
        cmds.text(l="strength")
        self.widgets.append(self.nextWidget(FloatFld(0.,1000.,.01,3)))
        cmds.text(l="exponent")
        self.widgets.append(self.nextWidget(FloatFld(0.,5.,.01,2)))
        cmds.text(l="")
        cmds.text(l="max age")
        self.widgets.append(self.nextWidget(FloatFld(0.,1000.,.01,2)))
        cmds.text(l="max distal")
        self.widgets.append(self.nextWidget(FloatFld(0.,5000.,.01,2)))
        cmds.setParent("..")

class BPIGrp(CheckBoxGrp):

    def __init__(self, cbLabel):

        CheckBoxGrp.__init__(self, cbLabel)

    def create(self, *_):

        self.widgets.append(self.nextCheckBox())
        cmds.text(l="res")
        self.widgets.append(self.nextWidget(IntFld(1,100,1)))
        cmds.text(l="density")
        self.widgets.append(self.nextWidget(FloatFld(.01,1.,.1,2)))

class WindSphereSpiral(EmptyGrp):

    def __init__(self):
        
        EmptyGrp.__init__(self)

    def create(self, *_):

        cmds.frameLayout(l="Wind Sphere Spiral",cll=1,cl=1,w=420)
        cmds.rowColumnLayout(nc=2,cw=[(1,90),(2,40)])
        cmds.text(l="spiral height: ")
        self.widgets.append(self.nextWidget(FloatFld(0., 1000., .2, 1)))
        cmds.setParent("..")
        cmds.columnLayout(w=225)
        cmds.text(l="Wind Spheres",fn="boldLabelFont")
        cmds.setParent("..")
        cmds.rowColumnLayout(nc=6,cw=[(1,70),(2,30),(3,30),(4,70),(5,30),(6,30)])
        cmds.text(l="radii: ")
        self.widgets.append(self.nextWidget(FloatFld(.1, 1000., .2, 1)))
        self.widgets.append(self.nextWidget(FloatFld(.1, 1000., .2, 1)))
        cmds.text(l="center dist: ")
        self.widgets.append(self.nextWidget(FloatFld(.1, 1000., .1, 2)))
        self.widgets.append(self.nextWidget(FloatFld(.1, 1000., .1, 2)))
        cmds.text(l="wind azi: ")
        self.widgets.append(self.nextWidget(FloatFld(.1, 3.13, .01, 2)))
        self.widgets.append(self.nextWidget(FloatFld(.1, 3.13, .01, 2)))
        cmds.text(l="wind str: ")
        self.widgets.append(self.nextWidget(FloatFld(0., 1., .01, 2)))
        self.widgets.append(self.nextWidget(FloatFld(0., 1., .01, 2)))
        cmds.text(l="height incr: ")
        self.widgets.append(self.nextWidget(FloatFld(.05, 50., .1, 1)))
        self.widgets.append(self.nextWidget(FloatFld(.05, 50., .1, 1)))
        cmds.text(l="polar incr: ")
        self.widgets.append(self.nextWidget(FloatFld(.1, 3.13, .01, 2)))
        self.widgets.append(self.nextWidget(FloatFld(.1, 3.13, .01, 2)))
        cmds.setParent("..")
        cmds.setParent("..")