# In this example, we create a very simple GUI class for Maya that utilizes a CmdUI object 
# to create UI components, save and load the settings of those components, and call a command

# This file should be stored in your Maya scripts path.  The module
#   files should be in a subdirectory.  Here, the subdirectory is Command_UI

import maya.cmds as cmds
import importlib
from Command_UI import ( flag as cf, cmdui, widget as widg)

# Create the CmdUI object, specifying the name of the Maya command, Maya's scripts directory (should be
#   the same as the directory for this file), directory for saving/loading, and list of Flags
# Here we are using the 'curve' command: https://download.autodesk.com/us/maya/2010help/CommandsPython/curve.html
#   with only the 'p' (point) and 'd' (degree) parameters set
curveCommand = cmdui.CmdUI(
    "curve",
    "C:/Users/<username>/Documents/maya/scripts/",
    "C:/Users/<username>/Documents/maya/scripts/CurveCommandPresets",
    [
        cf.FlagSingle("d",widg.FloatFld(3.,100000.,.01,2)),
        cf.FlagMulti("p",widg.EquiGrp(widg.FloatFld(-10000., 10000.,.01,2),3)),
    ]
)

# Import the file just created by the curveCommand
import curve_call
importlib.reload(curve_call)

class GUI:

    def __init__(self, *_):

        mainWindowName= "ExampleWindow"
        if(cmds.window(mainWindowName, exists=True)):
            cmds.deleteUI(mainWindowName)

        guiWidth = 300
        mainWindow = cmds.window("ExampleWindow", title="Example Window", w=guiWidth)

        cmds.scrollLayout(w=guiWidth)

        cmds.columnLayout(rs=5)

        cmds.rowColumnLayout(nc=2,cw=[(1,guiWidth/2),(2,guiWidth/2)])
        cmds.text(l="Current Preset: ")
        self.presetNameFld = cmds.textField()
        cmds.button(label="Save",w=50,command=self.callSave)
        cmds.button(label="Load",w=50)

        # Creates a popup menu that will display the list of settings files in the directory specified for the command.
        # This will be displayed when the Load button is left clicked.
        # The function passed will be triggered whenever a new menu item is selected. i.e. whenever a new preset is 
        #   loaded.  The function is not required. 
        curveCommand.makePresetsPopupMenu(self.setCurrentPreset)

        cmds.setParent("..")

        cmds.separator(h=5)

        cmds.rowColumnLayout(nc=2,cw=[(1,70),(2,35)])
        cmds.text("degree: ")
        curveCommand.flagUIs["d"].createUI()
        cmds.setParent("..")

        cmds.text("points")

        cmds.rowColumnLayout(nc=3, cw=[(1,40),(2,40),(3,40)])
        curveCommand.flagUIs["p"].createUI([0.,0.,0.])
        curveCommand.flagUIs["p"].createUI([0.,0.,0.])
        curveCommand.flagUIs["p"].createUI([0.,0.,0.])
        curveCommand.flagUIs["p"].createUI([0.,0.,0.])
        cmds.setParent("..")

        cmds.button(l="Make Curve",w=100,command=self.callCurveCommand)

        cmds.showWindow(mainWindow)

    def callSave(self, *_):

        presetName = cmds.textField(self.presetNameFld, q=True, tx=True)
        curveCommand.saveSettings(presetName)

    def callCurveCommand(self, *_):

        curve_call.call(curveCommand)

    def setCurrentPreset(self, *_):

        cmds.textField(self.presetNameFld, e=True, tx=curveCommand.currentPreset)