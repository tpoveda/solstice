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

import weakref

import maya.cmds as cmds

import solstice_pickerColors as colors

# Different states for the buttons
NORMAL, DOWN, DISABLED, SELECTED = 1, 2, 3, 4
INNER, OUTER = 1, 2

class solstice_pickerBaseButton(QPushButton, object):

    def __init__(self,
                 x=0,
                 y=0,
                 innerColor=colors.yellow,
                 outerColor=colors.blue,
                 glowColor=colors.red,
                 text=None,
                 control='',
                 enabled=True,
                 toggle=False,
                 parentCtrl=None,
                 parent=None,
                 btnInfo=None):
        super(solstice_pickerBaseButton, self).__init__(parent=parent)

        self._innerColor = innerColor
        self._outerColor = outerColor
        self._glowColor = glowColor
        self._text = text
        self._toggle = toggle
        self._control = control
        self._parentCtrl = parentCtrl
        self._childCtrls = []
        self._hierarchy = []
        self._btnInfo = btnInfo

        self._scene = None
        self._contextMenu = None

        self.move(x, y)

        self.setStyleSheet('background-color: rgba(0,0,0,0);')

        # Set the font for the button
        self._font = QFont()
        self._font.setPointSize(8)
        self._font.setFamily('Calibri')
        self.setFont(self._font)
        self._fontMetrics = QFontMetrics(self._font)

        self._pressed = False
        self._enabled = enabled
        self._hover = False
        self._selected = False

        self._glowIndex = 0
        self._animTimer = QTimer()
        #self._animTimer.timeout.connect(self._animateGlow)

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

        self._brushClear = QBrush(QColor(0, 0, 0, 0))
        self._brushBorder = QBrush(QColor(9, 10, 12))

    def addChild(self, btn):
        self._childCtrls.append(weakref.ref(btn))

    def getInfo(self):
        return self._btnInfo

    def setInfo(self, btnInfo):
        self._btnInfo = btnInfo
        self.move(btnInfo['x'], btnInfo['y'])
        self._text = btnInfo['text']

    def setControl(self, ctrl):
        self._control = ctrl

    def setParentControl(self, parentCtrl):
        self._parentCtrl = parentCtrl

    def scene(self):
        return self._scene()

    def setScene(self, scene):
        self._scene = weakref.ref(scene)

    def _updateColorsInfo(self):

        # Update glow range colors
        for i in range(1, self._glowSteps):
            for j in range(len(self._alphaRange)):
                newColor = self._glowColor
                newColor.setAlpha(i * self._alphaRange[j])
                self._glowPens.append(QPen(newColor, self._alphaType[j], Qt.SolidLine))

        # Update gradient colors
        innerGradient = QLinearGradient(0, 3, 0, 24)
        innerGradient.setColorAt(0, self._innerColor)
        innerGradient.setColorAt(1, self._innerColor.darker(200))
        self._gradient[NORMAL][INNER] = QBrush(innerGradient)

        outerGradient = QLinearGradient(0, 2, 0, 25)
        outerGradient.setColorAt(0, self._outerColor.darker(800))
        outerGradient.setColorAt(1, self._outerColor.darker(900))
        self._gradient[NORMAL][OUTER] = QBrush(outerGradient)

        innerGradientDown = QLinearGradient(0, 3, 0, 24)
        innerGradientDown.setColorAt(0, self._innerColor.darker(400))
        innerGradientDown.setColorAt(1, self._innerColor.darker(650))
        self._gradient[DOWN][INNER] = QBrush(innerGradientDown)

        outerGradientDown = QLinearGradient(0, 2, 0, 25)
        outerGradientDown.setColorAt(0, self._outerColor.darker(800))
        outerGradientDown.setColorAt(1, self._outerColor.darker(925))
        self._gradient[DOWN][OUTER] = QBrush(outerGradientDown)

        innerGradientDisabled = QLinearGradient(0, 3, 0, 24)
        innerGradientDisabled.setColorAt(0, self._innerColor.darker(850))
        innerGradientDisabled.setColorAt(1, self._innerColor.darker(950))
        self._gradient[DISABLED][INNER] = QBrush(innerGradientDisabled)

        outerGradientDisabled = QLinearGradient(0, 2, 0, 25)
        outerGradientDisabled.setColorAt(0, self._outerColor.darker(800))
        outerGradientDisabled.setColorAt(1, self._outerColor.darker(950))
        self._gradient[DISABLED][OUTER] = QBrush(outerGradientDisabled)

        innerGradientSelected = QLinearGradient(0, 3, 0, 24)
        innerGradientSelected.setColorAt(0, self._innerColor.darker(300))
        innerGradientSelected.setColorAt(1, self._innerColor.darker(400))
        self._gradient[SELECTED][INNER] = QBrush(innerGradientSelected)

        outerGradientSelected = QLinearGradient(0, 2, 0, 25)
        outerGradientSelected.setColorAt(0, self._outerColor.darker(500))
        outerGradientSelected.setColorAt(1, self._outerColor.darker(800))
        self._gradient[SELECTED][OUTER] = QBrush(outerGradientSelected)

    def _getCurrentGradientOffset(self):

        """
        Returns a correct gradient color and offset depending of the state of the button
        """

        if self._toggle:
            if self._pressed:
                gradient = self._gradient[DOWN]
                offset = 1
            else:
                gradient = self._gradient[NORMAL]
                offset = 0
        else:
            gradient = self._gradient[NORMAL]
            offset = 0
            if self.isDown():
                gradient = self._gradient[DOWN]
                offset = 1
            elif not self.isEnabled():
                gradient = self._gradient[DISABLED]

        return gradient, offset

    def paintBorder(self, painter, x, y, width, height):

        """
        Override this method to draw the border of the button
        """

        pass

    def paintOuter(self, painter, x, y, width, height):

        """
        Override this method to draw the outer part of the button
        """

        pass

    def paintInner(self, painter, x, y, width, height):

        """
        Override this method to draw the outer part of the button
        """

        pass


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

        painter.setBrush(self._brushBorder)
        painter.setPen(self._pensBorder)

        self.paintBorder(painter, x, y, width, height)

        painter.setPen(self._pensClear)
        painter.setBrush(gradient[OUTER])

        self.paintOuter(painter, x, y, width, height)

        painter.setBrush(gradient[INNER])

        self.paintInner(painter, x, y, width, height)

        # Paint text
        if self._text != '':
            textWidth = self._fontMetrics.width(self._text)
            textHeight = self._font.pointSize()

            textPath = QPainterPath()
            textPath.addText((width - textWidth) / 2, height - ((height - textHeight) / 2) - 1 + offset, self._font, self._text)
            glowIndex = self._glowIndex

            glowPens = self._glowPens

            alignment = (Qt.AlignCenter | Qt.AlignVCenter)

            if self.isEnabled():
                painter.setPen(self._pensShadow)
                painter.drawPath(textPath)

                painter.setPen(self._pensText)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

                if glowIndex > 0:
                    for index in range(3):
                        painter.setPen(glowPens[glowIndex][index])
                        painter.drawPath(textPath)

                    painter.setPen(glowPens[glowIndex][3])
                    painter.drawText(x, y + offset, width, height, alignment, self._text)
            else:
                painter.setPen(self._pensShadowDisabled)
                painter.drawPath(textPath)
                painter.setPen(self._pensTextDisabled)
                painter.drawText(x, y + offset, width, height, alignment, self._text)

    def mousePressEvent(self, event):
        super(solstice_pickerBaseButton, self).mousePressEvent(event)

        if self._control != '' and self._control is not None:
            modifiers = cmds.getModifiers()
            shift = (modifiers & 1) > 0
            ctrl = (modifiers & 4) > 0

            cmds.select(self._control, add=shift, deselect=ctrl)

    def mouseDoubleClickEvent(self, event):
        super(solstice_pickerBaseButton, self).mouseDoubleClickEvent(event)
        self._selectHierarchy()

    def _selectHierarchy(self):
        if len(self._hierarchy) > 0:
            for btn in self._hierarchy:
                if btn == self._control:
                    pass
                else:
                    cmds.select(btn, add=True)

    def updateHierarchy(self):
        self._hierarchy = self.getHierarchy()

    def getHierarchy(self):
        hierarchy = [self._control]
        if len(self._childCtrls) > 0:
            for child in self._childCtrls:
                hierarchy.extend(child().getHierarchy())
        return hierarchy

    def contextMenuEvent(self, event):
        pass