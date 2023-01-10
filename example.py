# In this example, we will create a very simple GUI class for Maya that utilizes a Cmd_UI object 
# to create UI components, save and load the settings of those components, and call a command

import maya.cmds as cmds
import widgetWrappers as widg, commandParameter as cp, cmd_UI

curveCommand = cmd_UI.Cmd_UI(
    "curve",
    "C:/Users/13308/Documents/maya/scripts/CurveCommandPresets",
    cp.CP_Single("d",widg.FloatFld(3.,100000.,.01,2)),
    cp.CP_Multi("p",widg.EquiGrp(widg.FloatFld(-10000., 10000.,.01,2),3)),
    cp.CP_Multi("ep",widg.EquiGrp(widg.FloatFld(-10000., 10000.,.01,2),3)))

