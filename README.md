# Command_UI
 
A set of classes designed to assist with the development of GUI plug-ins for Autodesk Maya.  In particular, these are designed for creating GUI's which involve many Maya command calls and/or commands with long lists of flags where it is useful to save and load values of GUI components associated with those flags.

This consists of a hierarchical composition, where CmdUI aggregates Flag, and Flag aggregates Widget.  Widget based objects wrap various GUI creation commands from Maya's Python API, i.e. intField, checkBox, etc.

Understanding requires some familiarity with Maya and the maya.cmds Python library.  For documentation on these, visit https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-Scripting/files/GUID-703B18A2-89E5-48A8-988A-1ED815D5566F-htm.html - Especially, the 'Python in Maya' and 'Using Python' links
