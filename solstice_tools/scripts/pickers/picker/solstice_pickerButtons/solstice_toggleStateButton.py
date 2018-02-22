#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_toggleStateButton.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Button that has a toggle that change its behaviour depending of
# a the value of an associated toggle button
# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import maya.cmds as cmds

from .. import solstice_pickerColors as colors
from .. import solstice_pickerBaseButton as baseBtn
import solstice_toggleButton as toggle
from .. import solstice_pickerUtils as utils

class solstice_toggleStateButton(baseBtn.solstice_pickerBaseButton, object):

    onOffToggle = Signal()
    onOffUntoggle = Signal()

    def __init__(
            self,x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None, onText='ON', offText='OFF'):

        super(solstice_toggleStateButton, self).__init__(
            x=x,
            y=y,
            text=text,
            radius=cornerRadius,
            width=width,
            height=height,
            innerColor=colors.black,
            btnInfo=btnInfo,
            parent=parent,
            buttonShape=baseBtn.solstice_pickerButtonShape.roundedSquare
        )

    def setInfo(self, btnInfo):
        super(solstice_toggleStateButton, self).setInfo(btnInfo)

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

    def postCreation(self):

        """
        This method is called after the button is addded to the picker scene
        """

        # self.updateState()
        # self.getPart().fkSignal.connect(self.updateState)
        # self.getPart().ikSignal.connect(self.updateState)

        self.onOffBtn = toggle.solstice_toggleButton(
            x=116,
            y=52,
            radius=2,
            text='GIMBAL',
            onText='ON',
            offText='OFF'
        )
        self.onOffBtn.setWidth(32)
        self.onOffBtn.setHeight(20)
        self.setInnerColor([100,100,100])
        self.setGlowColor([255,255,255])

        self._scene.addButton(self.onOffBtn)


