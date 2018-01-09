#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_commandButton.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Button classes for buttons that executes commands
# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

from .. import solstice_pickerColors as colors
from .. import solstice_pickerBaseButton as baseBtn
from .. import solstice_pickerUtils as utils


class solstice_commandButton(baseBtn.solstice_pickerBaseButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):

        super(solstice_commandButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            innerColor=colors.blue,
            btnInfo=btnInfo,
            parent=parent,
            buttonShape=baseBtn.solstice_pickerButtonShape.roundedSquare
        )

    def setInfo(self, btnInfo):
        super(solstice_commandButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])
        self.setRadius(btnInfo['radius'])
        self.setGizmo(btnInfo['gizmo'])
        self.setPart(btnInfo['part'])
        self.setSide(btnInfo['side'])
        self.setFkIkControl(btnInfo['FKIKControl'])
        self.setCommand(btnInfo['command'])
        if btnInfo['color'] != None:
            self.setInnerColor(btnInfo['color'])
        if btnInfo['glowColor'] != None:
            self.setGlowColor(btnInfo['glowColor'])


    @utils.pickerUndo
    def executeCommand(self):
        print('Executing command ...')
        exec(self._command)

    def mousePressEvent(self, event):
        self.executeCommand()
