#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerBaseButton.py
by Tomás Poveda
Custom button used by the picker of Solstice Short Film
______________________________________________________________________
Base class to be used in the buttons for the pickers
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import os

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mayaUtils

from pickers.picker import solstice_pickerColors as colors
from pickers.picker import solstice_pickerUtils as utils
from pickers.picker import solstice_pickerCommands as commands
from pickers.picker import solstice_pickerWindow


class solstice_pickerButtonShape(object):
    circular = 'circular',
    roundedSquare = 'roundedSquare'

# Different states for the buttons
NORMAL, DOWN, DISABLED, SELECTED = 1, 2, 3, 4
INNER = 1, 2

class solstice_pickerBaseButton(QPushButton, object):

    scriptsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts')

    def __init__(self,
                 x=0,
                 y=0,
                 innerColor=colors.yellow,
                 outerColor=colors.blue,
                 glowColor=colors.red,
                 text=None,
                 radius=25,
                 control='',
                 gizmo='',
                 part='',
                 side='',
                 enabled=True,
                 parentCtrl=None,
                 parent=None,
                 btnInfo=None,
                 buttonShape = solstice_pickerButtonShape.circular,
                 gradientIntensity = 0.6,
                 width=15,
                 height=5):
        super(solstice_pickerBaseButton, self).__init__(parent=parent)

        #print 'Creating button with control {0}'.format(control)

        # Color attributes
        self._innerColor = innerColor
        self._outerColor = outerColor
        self._glowColor = glowColor
        self._gradientIntensity = gradientIntensity
        self._brushClear = QBrush(QColor(0, 0, 0, 0))
        self._brushBorder = QBrush(QColor(9, 10, 12))

        # Controls attributes
        self._control = control
        self._parentCtrl = parentCtrl
        self._childCtrls = []
        self._hierarchy = []

        # Control info attributes
        self._btnInfo = btnInfo
        self._part = part
        self._side = side

        # Button shape attributes
        self._shape = buttonShape
        self._radius = radius

        # Button font attributes
        self._font = QFont()
        self._font.setPointSize(8)
        self._font.setFamily('Calibri')
        self.setFont(self._font)
        self._fontMetrics = QFontMetrics(self._font)

        # Button state attributes
        self._pressed = False
        self._enabled = enabled
        self._hover = False
        self._selected = False

        # Glow animation and color attributes
        self._glowIndex = 0
        self._animTimer = QTimer()
        self._animTimer.timeout.connect(self._animateGlow)
        self._glowPens = []
        self._gradient = {NORMAL: {}, DOWN: {}, DISABLED: {}, SELECTED: {}}
        self._glowSteps = 11
        self._alphaRange = [12.0, 5.0, 2.0, 25.5]
        self._alphaType = [1, 3, 5, 1]
        self._updateColorsInfo()
        self._pensBorder = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pensClear = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pensText = QPen(QColor(202, 207, 210), 1, Qt.SolidLine)
        self._pensShadow = QPen(QColor(9, 10, 12), 1, Qt.SolidLine)
        self._pensTextDisabled = QPen(QColor(102, 107, 110), 1, Qt.SolidLine)
        self._pensShadowDisabled = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)

        # Extras attributes
        self._text = text
        self._gizmo = gizmo
        self._scene = None
        self._contextMenu = None
        self._fkIkControl = None

        if self._shape == solstice_pickerButtonShape.circular:
            self.setFixedHeight(radius)
            self.setFixedWidth(radius)
        elif self._shape == solstice_pickerButtonShape.roundedSquare:
            self.setFixedHeight(height)
            self.setFixedWidth(width)
        self.move(x, y)
        self.setStyleSheet('background-color: rgba(0,0,0,0);')

    # ---------------------------------------------------------------------------------------------------------
    # ===== PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------

    @property
    def control(self):
        if self._scene._namespace != '':
            return self._scene._namespace+':'+self._control
        else:
            return self._control

    @property
    def controlGroup(self):
        if self._scene._namespace != '':
            if self._side != '':
                return self._scene._namespace+':'+self._side.upper()+'_'+self._part+'_ctrlsGrp'
            else:
                return self._scene._namespace + ':' + self._part + '_ctrlsGrp'
        else:
            if self._side != '':
                return self._side.upper()+'_'+self._part+'_ctrlsGrp'
            else:
                return self._part+'_ctrlsGrp'

    def setNamespace(self, namespace):
        # TODO: Create a most solid way if a current existing control has a namespace
        # an update it if necessary
        self._namespace = namespace
        if self._namespace == '':
            if ':' in self._control:
                self._control = self._control.split(':')[1]
        else:
            self._control = self._namespace + ':' + self._control

    def addChild(self, btn):

        """
        Add a child to the list of childs of the button
        """

        self._childCtrls.append(btn)

    def getInfo(self):

        """
        Return info of the button
        """

        return self._btnInfo

    def getPart(self):

        """
        Returns the pickerPart associated to this button
        """

        for part in self._scene._parts:
            if part.name == self._part and part.side == self._side:
                return part

    def setInfo(self, btnInfo):

        """
        Set the new button info and set the properties of the button
        """

        self._btnInfo = btnInfo
        self.move(btnInfo['x'], btnInfo['y'])
        self._text = btnInfo['text']

    def setControl(self, ctrl):

        """
        Set the control that this button selects
        """

        self._control = ctrl

    def setParentControl(self, parentCtrl):

        """
        Sets the parent control of this control
        """

        self._parentCtrl = parentCtrl

    def setFkIkControl(self, fkIkCtrl):

        """
        Set the FKIK control associated to this button
        This control is selected when we change from IK to FK and viceversa
        """

        self._fkIkControl = fkIkCtrl


    def setCommand(self, command):

        """
        Set the Python command to execute when the button is pressed
        :param command: str, python command
        """

        self._command = command
        

    def setInnerColor(self, innerColor):

        """
        Sets the inner color of the button
        """

        if type(innerColor) == list:
            innerColor = QColor.fromRgb(innerColor[0], innerColor[1], innerColor[2])
        self._innerColor = innerColor
        self._updateColorsInfo()

    def setGlowColor(self, glowColor):

        """
        Sets the glow color of the button
        """

        if type(glowColor) == list:
            glowColor = QColor.fromRgb(glowColor[0], glowColor[1], glowColor[2])
        self._glowColor = glowColor
        self._updateColorsInfo()

    def scene(self):

        """
        Returns the QSceneWidget that this contorl belongs to
        """
        return self._scene()

    def setScene(self, scene):

        """
        Sets the scene of this button
        """

        self._scene = scene

    def setPart(self, part):

        """
        Sets the rig part that this button belongs to
        """

        self._part = part

    def setSide(self, side):

        """
        Sets the side of this button
        """

        self._side = side

    def setGizmo(self, gizmo):

        """
        Sets the gizmo that must be activated when we press the button
        """

        self._gizmo = gizmo

    def getFkIkControl(self):

        """
        Get the fkik control associated to this button
        """

        return self._fkIkControl

    def getRadius(self):

        """
        Get the radius of the button
        """

        return self._radius

    def setRadius(self, radius):

        """
        Set the radius of the button
        """

        self._radius = radius

        if self._shape == solstice_pickerButtonShape.circular:
            self.setFixedWidth(radius)
            self.setFixedHeight(radius)

    def getGradientIntensity(self):

        """
        Get the gradient intensity
        """

        return self._gradientIntensity


    def setGradientIntensity(self, gradientIntensity):

        """
        Set the gardient intensity
        """

        self._gradientIntensity = gradientIntensity
        self._updateColorsInfo()

    def setWidth(self, width):

        """
        Set the width of the button
        """

        self.setFixedWidth(width)

    def setHeight(self, height):

        """
        Set the height of the button
        """

        self.setFixedHeight(height)

    def updateHierarchy(self):

        """
        Updates the hierarchy of the button
        """
        self._hierarchy = self.getHierarchy()

    def getHierarchy(self):

        """
        Get the hierarchy of the button by recursion
        """

        # NOTE: If the system fails with a maximum recursion error check that the parent
        # name is corret and not is equal as the name of the control

        hierarchy = [self.control]
        if len(self._childCtrls) > 0:
            for child in self._childCtrls:
                if child == self.control:
                    continue
                hierarchy.extend(child.getHierarchy())
        return hierarchy

    # ---------------------------------------------------------------------------------------------------------
    # ===== PRIVATE METHODS
    # ---------------------------------------------------------------------------------------------------------

    def _updateColorsInfo(self):

        """
        Updates the color info of the button
        """

        # Update glow range colors
        for i in range(1, self._glowSteps):
            for j in range(len(self._alphaRange)):
                newColor = self._glowColor
                newColor.setAlpha(i * self._alphaRange[j])
                self._glowPens.append(QPen(newColor, self._alphaType[j], Qt.SolidLine))

        # Update gradient colors
        innerGradient = QLinearGradient(0, 3, 0, 24)
        innerGradient.setColorAt(0, self._innerColor)
        innerGradient.setColorAt(1, self._innerColor.darker(200*self._gradientIntensity))
        self._gradient[NORMAL][INNER] = QBrush(innerGradient)

        innerGradientDown = QLinearGradient(0, 3, 0, 24)
        innerGradientDown.setColorAt(0, self._innerColor.darker(400*self._gradientIntensity))
        innerGradientDown.setColorAt(1, self._innerColor.darker(650*self._gradientIntensity))
        self._gradient[DOWN][INNER] = QBrush(innerGradientDown)

        innerGradientDisabled = QLinearGradient(0, 3, 0, 24)
        innerGradientDisabled.setColorAt(0, self._innerColor.darker(850*self._gradientIntensity))
        innerGradientDisabled.setColorAt(1, self._innerColor.darker(950*self._gradientIntensity))
        self._gradient[DISABLED][INNER] = QBrush(innerGradientDisabled)

        innerGradientSelected = QLinearGradient(0, 3, 0, 24)
        innerGradientSelected.setColorAt(0, self._innerColor.darker(300*self._gradientIntensity))
        innerGradientSelected.setColorAt(1, self._innerColor.darker(400*self._gradientIntensity))
        self._gradient[SELECTED][INNER] = QBrush(innerGradientSelected)

    def _getCurrentGradientOffset(self):

        """
        Returns a correct gradient color and offset depending of the state of the button
        """
        gradient = self._gradient[NORMAL]
        offset = 0
        if self.isDown():
            gradient = self._gradient[DOWN]
            offset = 1
        elif not self.isEnabled():
            gradient = self._gradient[DISABLED]

        return gradient, offset

    def _animateGlow(self):

        """
        Animates the glow of the button text
        """

        if self._hover:
            if self._glowIndex >= self._glowSteps-1:
                self._glowIndex = self._glowSteps-1
                self._animTimer.stop()
            else:
                self._glowIndex += 1
        else:
            self._glowIndex = 0
            self._animTimer.stop()
        mayaUtils.executeDeferred(self.update)

    def _startGlowAnim(self):

        """
        Start the glow animation
        """

        if self._animTimer.isActive(): return

        self._animTimer.start(20)

    @utils.pickerUndo
    def _selectHierarchy(self):

        """
        Select the hierarchy of the button
        """

        if len(self._hierarchy) > 0:
            for btn in self._hierarchy:
                if btn == self.control:
                    pass
                else:
                    window_picker = solstice_pickerWindow.window_picker
                    if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
                        btn = '{0}:{1}'.format(window_picker.namespace.currentText(), btn)
                    cmds.select(btn, add=True)

    @utils.pickerUndo
    def _resetControl(self):

        """
        Reset the control the its default values
        """

        for axis in ['x', 'y', 'z']:
            for xform in ['t', 'r', 's']:
                try:
                    newVal = 0.0
                    if xform == 's':
                        newVal = 1.0
                    cmds.setAttr(self.control + '.' + xform + axis, newVal)
                except:
                    pass

    @utils.pickerUndo
    def _mirrorControl(self):

        """
        Mirror control attributes from one side to another
        """

        mirror_ctrl = utils.getMirrorControl(self.control)

        print(mirror_ctrl)

        if mirror_ctrl is None:
            return
        newXForm = {}
        for xform in ['t', 'r', 's']:
            newXForm[xform] = {}
            for axis in ['x', 'y', 'z']:
                newXForm[xform][axis] = cmds.getAttr(self.control + '.' + xform + axis)

        for xform, value in newXForm.items():
            for axis, xformValue in value.items():
                try:
                    cmds.setAttr(mirror_ctrl + '.' + xform + axis, xformValue)
                except:
                    pass

    @utils.pickerUndo
    def _flipControl(self):

        """
        Flip control attributes between sides
        """

        mirrorCtrl = utils.getMirrorControl(self.control)
        if mirrorCtrl is None:
            return

        origXForm = {}
        mirrorXForm = {}

        for xform in ['t', 'r', 's']:
            origXForm[xform] = {}
            for axis in ['x', 'y', 'z']:
                origXForm[xform][axis] = cmds.getAttr(self.control + '.' + xform + axis)
        for xform in ['t', 'r', 's']:
            mirrorXForm[xform] = {}
            for axis in ['x', 'y', 'z']:
                mirrorXForm[xform][axis] = cmds.getAttr(mirrorCtrl + '.' + xform + axis)

        for xform, value in origXForm.items():
            for axis, xformValue in value.items():
                try:
                    cmds.setAttr(mirrorCtrl + '.' + xform + axis, xformValue)
                except:
                    pass
        for xform, value in mirrorXForm.items():
            for axis, xformValue in value.items():
                try:
                    cmds.setAttr(self.control + '.' + xform + axis, xformValue)
                except:
                    pass


    @utils.pickerUndo
    def _resetControlAtributes(self):

        """
        Reset the attributes of the control
        """

        commands.resetAttributes(self.control)

    # ---------------------------------------------------------------------------------------------------------
    # ===== OVERRIDE METHODS
    # ---------------------------------------------------------------------------------------------------------

    def paintInner(self, painter, x, y, width, height):

        """
        Draw the iner part of the button
        """

        if self._shape == solstice_pickerButtonShape.circular:
            painter.drawEllipse(QRect(x+1, y+1, width-1, height-1))
        else:
            painter.drawRoundedRect(QRect(x + 2, y + 2, width - 4, height - 4), self._radius-1, self._radius-1)

    def paintEvent(self, *args):

        painter = QStylePainter(self)
        option = QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width = option.rect.width() - 1

        # Paint button
        painter.setRenderHint(QPainter.Antialiasing)

        gradient, offset = self._getCurrentGradientOffset()

        painter.setPen(self._pensBorder)
        painter.setBrush(gradient[INNER])
        self.paintInner(painter, x, y, width, height)

        # if self._selected:
        #     gradient = self._gradient[SELECTED]
        #     painter.setBrush(self._brush_border)
        #     painter.setPen(self._pens_border)
        #
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 1, y + 1, width - 1, height - 1))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 1, y + 1, width - 1, height - 1), self._radius, self._radius)
        #
        #     painter.setPen(self._pens_clear)
        #
        #     painter.setBrush(gradient[OUTER])
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 2, y + 2, width - 3, height - 3))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 2, y + 2, width - 3, height - 3), self._radius, self._radius)
        #
        #     painter.setBrush(gradient[INNER])
        #     if self._type == 'circle':
        #         painter.drawEllipse(QRect(x + 3, y + 3, width - 5, height - 5))
        #     else:
        #         painter.drawRoundedRect(QRect(x + 3, y + 3, width - 5, height - 5), self._radius - 1, self._radius - 1)

        # Paint text
        if self._text != '':
            textWidth = self._fontMetrics.width(self._text)
            textHeight = self._font.pointSize()

            textPath = QPainterPath()
            textPath.addText((width - textWidth) / 2, height - ((height - textHeight) / 2) - 1 + offset, self._font, self._text)
            alignment = (Qt.AlignHCenter | Qt.AlignVCenter)

            glowIndex = self._glowIndex
            glowPens = self._glowPens

            if self.isEnabled():
                painter.setPen(self._pensShadow)
                painter.drawPath(textPath)

                painter.setPen(self._pensText)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

                if glowIndex > 0:
                    for index in range(3):
                        painter.setPen(glowPens[index])
                        painter.drawPath(textPath)
                    painter.setPen(self._glowColor)
                    painter.drawText(x, y + offset, width, height, alignment, self._text)
            else:
                painter.setPen(self._pensShadowDisabled)
                painter.drawPath(textPath)
                painter.setPen(self._pensTextDisabled)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

    def enterEvent(self, event):

        """
        Start ghe glow animation
        """

        super(solstice_pickerBaseButton, self).enterEvent(event)

        if not self.isEnabled(): return

        self._hover = True
        self._startGlowAnim()

    def leaveEvent(self, event):

        """
        End glow animation and restart button state
        """

        super(solstice_pickerBaseButton, self).leaveEvent(event)

        if not self.isEnabled(): return

        self._hover = False
        self._startGlowAnim()

    def mousePressEvent(self, event):

        """
        Select the control if it exists
        """

        super(solstice_pickerBaseButton, self).mousePressEvent(event)

        if self.control != '' and self.control is not None:
            modifiers = cmds.getModifiers()
            shift = (modifiers & 1) > 0
            ctrl = (modifiers & 4) > 0
            if cmds.objExists(self.control):
                cmds.select(self.control, add=shift, deselect=ctrl)

                if self._gizmo != '':
                    utils.setTool(self._gizmo)
            else:
                for side in ['L', 'R']:
                    if side+'_' in self.control:
                        self._control = self._control.replace(side+'_', '')
                        splits = self.control.split('_')
                        new_name = splits[0] + '_'+side
                        for i in xrange(len(splits)):
                            if i==0: continue
                            new_name += '_' + splits[i]
                            if cmds.objExists(new_name):
                                self._control = new_name
                                cmds.select(self.control, add=shift, deselect=ctrl)
                                return
                print 'Could not select control {0} because it does not exists in the scene'.format(self.control)

    def mouseDoubleClickEvent(self, event):

        """
        Select the hierarchy of the button
        """

        super(solstice_pickerBaseButton, self).mouseDoubleClickEvent(event)
        self._selectHierarchy()

    def contextMenuEvent(self, event):

        """
        Open the contextual menu of the button
        Override in subclasses
        """

        super(solstice_pickerBaseButton, self).contextMenuEvent(event)

    def postCreation(self):

        """
        This method is called after the button is addded to the picker scene
        Override in custom buttons
        """

        pass