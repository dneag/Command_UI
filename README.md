# Command_UI
 
A set of wrapper classes designed to assist with the development of python GUI plug-ins for Autodesk's Maya software.  
In particular, these are designed for creating GUI plug-ins which involve many Maya command calls and/or commands with 
long lists of parameters where it is useful to save and load values of GUI components associated with those parameters.

This consists of three tiers of classes.  The lowest are defined in widgetWrappers.py and are used to construct those
in commandParameter.py, which, in turn, construct Cmd_UI objects.