
import maya.cmds as cmds
import copy
import numpy as np

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

# Same purpose as a FlagMultiGradi, except instead of just getting all of the gradients' values,
# we fit the curves to polynomial functions
class FlagMultiGradiToPoly(FlagMulti):

    def __init__(self, shortName, baseWidget):
        
        # Range widgets are those that define the range of the gradient. These are used to scale the x axis
        # values so that the polynomials represent the correct range. It might be better to couple these 
        # with the actual gradient widgets, but for now this is just a parallel list that must line up 
        # with self.widgets in this class
        self.rangeWidgets = []
        FlagMulti.__init__(self, shortName, baseWidget)
    
    def createUI(self, rangeWidget, val=None):

        if rangeWidget: self.rangeWidgets.append(rangeWidget)
        return FlagMulti.createUI(self, val)
    
    def addRangeWidget(self, rangeWidget):

        self.rangeWidgets.append(rangeWidget)

    # Fit the curves to polynomial equations and return a list of strings representing them. 
    # Each order's gradient has multiple strings representing different attributes of the polynomial:
    #   string 1 - coefficients
    #   string 2 - limit intersections: the limit is 1 so these are intersections with y = 1. Each pair of elements
    #       represents the start x value, followed by the end x value, of a portion of the curve that is above 1.
    #   string 3 - minimum curves: points on the curve used to clip it at the running minimum while integrating
    # So the returned list looks like: [coefficients, limits, min curves, coefficients, limits, min curves, ...]
    def getParamVal(self, *_):

        if (len(self.widgets) != len(self.rangeWidgets)):
            cmds.error("The number of gradients for " + self.shortName + "(" + str(len(self.widgets)) + ") \
                       does not match the number of range values (" + str(len(self.rangeWidgets)) + ")")

        gradientsAsStrings = []
        
        for gradientWidget, rangeWidget in zip(self.widgets, self.rangeWidgets):

            # Check that the widget holding the range value is of the right type
            if cmds.objectTypeUI(rangeWidget) == 'floatField':
                rangeValue = cmds.floatField(rangeWidget, query=True, v=True)
            elif cmds.objectTypeUI(rangeWidget) == 'intField':
                rangeValue = cmds.intField(rangeWidget, query=True, v=True)
            else:
                cmds.error(self.shortName + " range widget must be floatField or intField")

            # Gather the values on the gradient at intervals of .01. (100 values total)
            xValue = 0.0
            y_values = []
            x_values = []
            while round(xValue, 2) <= 1.:
                y_values.append(cmds.gradientControlNoAttr(gradientWidget.uiID, q=True, vap=xValue))
                x_values.append(xValue * rangeValue)
                xValue += .01
            
            # Get the number of optionVars (control points) on the gradient.
            # getVal() returns all optionVars for the gradient represented as a string which is a concatenation of 
            # the values (y, x, and curve type) that make up individual option vars.  Since there are 3 per optionVar, divide by 3.
            numOptionVars = len(gradientWidget.getVal().split(',')) // 3

            # Fit the curve to a polynomial, then convert it to a string representing the coefficients.
            # Getting an accurate representation of the curve can be tricky, and I'm not sure it's possible
            # to get it perfect.  One thing I've noticed is that the degree needs to be sufficiently high, and
            # even curves that appear to be low degree will tend to fit better with a higher degree setting. So
            # let's use the value based on the optionVars but only if its greater than 8.
            npCoefficients = np.polyfit(x_values, y_values, max(numOptionVars, 8))
            
            # Print a nice string of the funcion that can be copied into a graphing calculator
            # print("coefficients for " + self.shortName + " with y values: ", y_values, "\n",
            #       self.__getCopyableCoefficientString(npCoefficients))
            
            coefficients = ",".join([ str(float(c)) for c in npCoefficients])
            gradientsAsStrings.append(coefficients)

            gradientsAsStrings.append(self.__getLimitIntersections(npCoefficients, 1., rangeValue))
                
            
            
            gradientsAsStrings.append(self.__getMinCurves(x_values, y_values))
        
        print("\ngradientsAsStrings for " + self.shortName + " " + str(len(gradientsAsStrings)) + "\n")
        for i in range(0, len(gradientsAsStrings), 3):
            print("coefficients " + gradientsAsStrings[i])
            print("1 intersects " + gradientsAsStrings[i+1])
            print("min curves " + gradientsAsStrings[i+2])

        return gradientsAsStrings
    
    def __getLimitIntersections(self, coeffs, limit, rangeValue):

        # Shift the curve vertically by 1 and find the roots within 0 and rangeValue, these are the curve's 
        # intersections with y = 1 and they are used to clip the curve at 1 when integrating
        shiftedCurve = coeffs.copy()
        shiftedCurve[-1] -= limit
        limitIntersections = np.roots(shiftedCurve)
        limitIntersections = [r.real for r in limitIntersections if np.isclose(r.imag, 0)]
        limitIntersections = [num for num in reversed(limitIntersections) if num >= 0 and num <= rangeValue]
        # Now we have the limit intersections and we want this list to show where the curve goes above and below the limit.
        # Since 'going above' and 'going below' will naturally alternate, we can just check the y value at 0., and call
        # it a 'going above' point if it is above the limit.
        if np.polyval(coeffs, 0.) > 1.:
            limitIntersections.insert(0,0.)
        
        return ",".join([ str(float(cx)) for cx in limitIntersections ])

    def __getMinCurves(self, xVals, yVals):

        # min_curves is used to clip the curve at the running minimum while integrating.  Each set of 3 elements
        # represents a point on the curve where we either just started going up from a new minimum y value, or
        # just started going down from the previous minimum. Whether it is up or down is indicated by the 
        # third in the set; 1 for up and -1 for down.  Ranges from a -1 to a 1 should be integrated
        # while ranges from a 1 to a -1 should only take the area under the y value at the start of the range.
        # Note that we're directly using the x and y values of the gradient, which may be slightly different than
        # the fitted curve, but I think this will be a sufficient approximation.
        min_curves = [ xVals[0], yVals[0], 1 if yVals[1] >= yVals[0] else -1  ]

        for i in range(1, len(xVals) - 1):
            if yVals[i+1] >= yVals[i] and min_curves[-1] == -1:
                min_curves.extend([xVals[i], yVals[i], 1])
            elif yVals[i+1] < yVals[i] and min_curves[-1] == 1 and yVals[i+1] < min_curves[-2]:
                min_curves.extend([xVals[i], yVals[i], -1])

        return ",".join([ str(m) for m in min_curves ])
    
        # Below is another method for getting min curves which uses the minima of the curve.  Results were funny.

        # min_curves is used to clip the curve at the running minimum while integrating. As with the limit
        # intersections list, this one will also mark points on the curve which are the start or end of an x
        # range which need not be integrated. Both x and y values are included since the y value is used as
        # the constant with which to multiply over the ranges that are above the running minimum.
        # first_derivative = np.polyder(coeffs)
        # critical_points = np.roots(first_derivative)
        # critical_points = critical_points[np.isreal(critical_points)].real
        # second_derivative = np.polyder(first_derivative)
        
        # # If the curve is moving up at x = 0., then this is the start of a range above the running minimum, so include it
        # upAtZero = np.polyval(coeffs, 0.) < np.polyval(coeffs, rangeValue / 50)
        # minima = [] if not upAtZero else [ 0., np.polyval(coeffs, 0.) ]
        # for x in reversed(critical_points):
        #     if x > rangeValue or x <= 0.:
        #         continue

        #     second_deriv_value = np.polyval(second_derivative, x)
        #     #print("second dderiv val: " + str(second_deriv_value))
        #     if second_deriv_value > 0:
        #         y = np.polyval(coeffs, x)
        #         if len(minima) == 0 or y < minima[-1]:
        #             #if (len(minima) > 0):
        #                 #print("is " + str(y) + " less than " + str(minima[-1]))
        #             minima.extend([x, y])

        # print("minima for " + self.shortName, minima)
        # # Now we have the running minimum minima (not a typo), these are the minima whose y values are lower than any
        # # previous minima on the curve.  These mark the starts of a range above the running minimum, but we still need
        # # a little more.  We need to find any points on the curve which begin to fall below their relative most recent minima.
        # # These will mark the end of a range above the running minimum.  To find these, we just need to find the point
        # # between each two minima that intersects with the y value of the first.  Note that for each subsequent pair of
        # # minima there will be just one of these points, and that the curve is always sloping down at this point.
        # min_curves = []
        # for i in range(0, len(minima), 2):
        #     x, y = minima[i], minima[i + 1]
        #     shiftedCurve = coeffs.copy()
        #     shiftedCurve[-1] -= y
        #     runningMinIntersections = np.roots(shiftedCurve)
        #     runningMinIntersections = [r.real for r in runningMinIntersections if np.isclose(r.imag, 0)]
        #     nextMinimaX = rangeValue if len(minima) <= i + 2 else minima[i + 2] 
        #     print("next minima x: " + str(nextMinimaX))
        #     runningMinIntersections = [num for num in reversed(runningMinIntersections) if num > x and num <= nextMinimaX] 
        #     if len(runningMinIntersections) > 1:
        #         print("multiple intersections between minima?: ", runningMinIntersections)
        #         rangeAboveMin = [x,y,runningMinIntersections[0]]
        #     elif len(runningMinIntersections) == 0:
        #         print("No min intersections? ")
        #         rangeAboveMin = [x,y,rangeValue]
        #     else:
        #         rangeAboveMin = [x,y,runningMinIntersections[0]]

        #     min_curves.extend(rangeAboveMin)

    def __getCopyableCoefficientString(self, coeffs):

        copyableCoefficientString = ""
        for i in range(len(coeffs)):
            exponent = len(coeffs) - i - 1
            pFloat = float(coeffs[i])
            formattedCoeff = str(f"{pFloat:.30f}")
            if i > 0 and pFloat >= 0.:
                formattedCoeff = "+" + formattedCoeff
            if exponent > 1:
                exponent = "x^"+str(exponent)
            elif exponent == 1:
                exponent = "x"
            else:
                exponent = ""
                    
            copyableCoefficientString += formattedCoeff + exponent 
        
        return copyableCoefficientString

# Allow adding a flag with no widget or values to save / load
class FlagMulti_NoWidget(Flag):

    def __init__(self, shortName):
        
        Flag.__init__(self, shortName)
        self.paramVal = None

    def setParamVal(self, val):

        self.paramVal = val
        
    def getParamVal(self, *_):

        return self.paramVal
    