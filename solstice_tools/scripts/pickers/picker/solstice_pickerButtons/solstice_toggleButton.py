#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_toggleButton.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Base class used to create a toggle behaviour button
# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

from pickers.picker import solstice_pickerColors as colors
from pickers.picker import solstice_pickerBaseButton as baseBtn

class solstice_toggleButton(baseBtn.solstice_pickerBaseButton, object):

    toggleOn = Signal()
    toggleOff = Signal()

    def __init__(self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None, onText='ON', offText='OFF'):

        btnText = text
        if text == '' or text == None:
            btnText = 'FK'

        super(solstice_toggleButton, self).__init__(
            x=x,
            y=y,
            text=btnText,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            innerColor=colors.blue,
            btnInfo=btnInfo,
            parent=parent,
            buttonShape=baseBtn.solstice_pickerButtonShape.roundedSquare
        )

        self._onText = text if onText == '' else onText
        self._offText = offText

    def setInfo(self, btnInfo):
        super(solstice_toggleButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setRadius(btnInfo['radius'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])
        self.setGizmo(btnInfo['gizmo'])
        self.setPart(btnInfo['part'])
        self.setSide(btnInfo['side'])
        if btnInfo['color'] != None:
            self.setInnerColor(btnInfo['color'])
        if btnInfo['glowColor'] != None:
            self.setGlowColor(btnInfo['glowColor'])

    def mousePressEvent(self, event):

        self._pressed = not self._pressed
        self.repaint()

        self.toggleOn.emit() if self._pressed == True else self.toggleOff.emit()

    def _getCurrentGradientOffset(self):

        """
        Returns a correct gradient color and offset depending of the state of the button
        """

        gradient = self._gradient[baseBtn.NORMAL]
        offset = 0
        if self._pressed:
            gradient = self._gradient[baseBtn.DOWN]
            offset = 1
        return gradient, offset

    def paintEvent(self, event):
        super(solstice_toggleButton, self).paintEvent(event)
        self._text = self._onText if self._pressed == True else self._offText