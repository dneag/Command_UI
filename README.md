# Command_UI
 
A set of wrapper classes designed to assist with the development of python GUI plug-ins for Autodesk's Maya software.  
In particular, these are designed for creating GUI's which involve many Maya command calls and/or commands with 
long lists of flags where it is useful to save and load values of GUI components associated with those flags.

This consists of three tiers of classes.  The lowest are defined in widget.py and are used to construct those
in flag.py, which, in turn, construct CmdUI objects.

Understanding requires some familiarity with Maya and the maya.cmds Python library

For documentation, visit https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-Scripting/files/GUID-703B18A2-89E5-48A8-988A-1ED815D5566F-htm.html - Especially, the 'Python in Maya' and 'Using Python' links