# In this example, we will create a very simple GUI class for Maya that utilizes a Cmd_UI object 
# to create UI components, save and load the settings of those components, and call a command

import maya.cmds as cmds
import importlib
from Command_UI import ( widgetWrappers as widg, commandParameter as cp, cmd_UI)
importlib.reload(widg)
importlib.reload(cp)
importlib.reload(cmd_UI)

curveCommand = cmd_UI.Cmd_UI(
    "curve",
    "C:/Users/13308/Documents/maya/scripts/CurveCommandPresets",
    [
    cp.CP_Single("d",widg.FloatFld(3.,100000.,.01,2)),
    cp.CP_Multi("p",widg.EquiGrp(widg.FloatFld(-10000., 10000.,.01,2),3)),
    cp.CP_Multi("ep",widg.EquiGrp(widg.FloatFld(-10000., 10000.,.01,2),3))
    ]
)

import curve_call
importlib.reload(curve_call)

class GUI:

    def __init__(self, *_):

        mainWindowName= "ExampleWindow"
        if(cmds.window(mainWindowName, exists=True)):
            cmds.deleteUI(mainWindowName)
        mainWindow = cmds.window("ExampleWindow", title="Example Window", w=300)
        cmds.scrollLayout(w=300)
        cmds.rowColumnLayout(nc=2,cw=[(1,70),(2,35)])
        cmds.text("degree: ")
        curveCommand.paramUIs["d"].createUI()
        cmds.setParent("..")
        cmds.separator()
        cmds.rowColumnLayout(nc=2,cw=[(1,150),(2,150)])
        cmds.text("points")
        cmds.text("edit points")
        cmds.rowColumnLayout(nc=3, cw=[(1,40),(2,40),(3,40)])
        curveCommand.paramUIs["p"].createUI()
        curveCommand.paramUIs["p"].createUI()
        curveCommand.paramUIs["p"].createUI()
        cmds.showWindow(mainWindow)