
import maya.cmds as cmds
import copy

# These classes bind a Maya command's parameter's 'short name' to one or more associated GUI elements
# The purpose is to simplify saving and loading of GUI's associated with commands with lots of parameters,
#   as well as the calls to those commands

# These are the middle tier in a set of wrappers designed for this purpose.
# The lowest, those defined in widgetWrappers.py, are passed to their constructors, while
#   these are passed to MayaCommandUI objects' constructors

class CP_Single:

    def __init__(self, shortName, widget):
        
        self.shortName = shortName
        self.widget = widget

    def createUI(self, *_):

        self.widget.create()

    def getParamVal(self, *_):

        return self.widget.getVal()
    
    def enable(self, enabled):

        self.widget.enable(enabled)

    def writeSettings(self, file):

        self.widget.writeVal(file, self.shortName)

    def loadSettings(self, file):

        self.widget.loadVal(file, self.shortName)

class CP_Orders(CP_Single):

    def __init__(self, shortName, widget):
        
        CP_Single.__init__(self, shortName, widget)

        self.ordersLayout = None
        self.orderFrameLayouts = []
        self.totalOrders = 4 # does not include leaf shoots

    def createUI(self, *_):

        self.widget.uiID = cmds.intField(   v=self.widget.min,min=self.widget.min,max=self.widget.max,
                                            s=self.widget.step,cc=self.updateLayouts)
    
    def getParamVal(self, *_):

        return super().getParamVal() + 1 # plus one for leaf shoots...

    def loadSettings(self, file):

        super().loadSettings(file)
        self.updateLayouts()
        
    def createOrdersLayout(self, *_):

        self.ordersLayout = cmds.frameLayout(l="Order Controls",cll=1,cl=0,w=420,ec=self.updateLayouts)

    def createNextOrderLayout(self, orderNum):

        self.orderFrameLayouts.append(cmds.frameLayout(l="Order " + str(orderNum+1),cll=1,cl=1,vis=1))

    def updateLayouts(self, *_):

        newOrderCount = self.widget.getVal()

        for i in range(self.totalOrders):

            visibility = 1 if i < newOrderCount else 0
            cmds.frameLayout(self.orderFrameLayouts[i], e=True, vis=visibility)

# The widget argument must be of one of the above types
# The number of initValues should correspond to the number of widgets to be created
class CP_Multi:

    def __init__(self, shortName, baseWidget):
        
        self.shortName = shortName
        self.baseWidget = baseWidget
        self.widgets = []

    def createUI(self, *_):

        self.widgets.append(copy.deepcopy(self.baseWidget))
        self.widgets[-1].create()

    def getParamVal(self, *_):

        value = []
        for widget in self.widgets:

            value.append(widget.getVal())

        return value

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
class CP_MultiGradi(CP_Multi):

    def __init__(self, shortName, baseWidget, valuesPerGradient):
        
        CP_Multi.__init__(self, shortName, baseWidget)

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

# Class specifically for the "igs" parameter.  Assumes baseWidget is an EquiGrp with 4 widgetsPerGroup and
# that there will be a total of 5 groups
class CP_IGS(CP_Multi):

    def __init__(self, shortName, baseWidget):
        
        CP_Multi.__init__(self, shortName, baseWidget)

        self.visibilities = [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 1, 1]]

    def createUI(self, *_):
        
        groupIndex = len(self.widgets)
        super().createUI()

        for i in range(len(self.widgets[groupIndex].widgets)):

            cmds.floatField(self.widgets[groupIndex].widgets[i].uiID, e=True, vis=self.visibilities[groupIndex][i])