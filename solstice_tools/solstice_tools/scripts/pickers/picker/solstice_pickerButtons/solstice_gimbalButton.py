#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_gimbalButton.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Specific button used to select gimbal elements on the body picker
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

import solstice_toggleStateButton as toggleState

class solstice_gimbalButton(toggleState.solstice_toggleStateButton, object):
    def __init__(
            self,x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None, onText='ON', offText='OFF'):

        super(solstice_gimbalButton, self).__init__(
            x=x,
            y=y,
            text=text,
            cornerRadius=cornerRadius,
            width=width,
            height=height,
            btnInfo=btnInfo,
            parent=parent,
            onText=onText,
            offText=offText
        )

    def updateState(self):

        """
        Update current state of the toggle button
        """

        fkIkState = self.getPart().getFKIK(asText=True)
        if fkIkState == 'IK':
            self._control = self._control.replace('fk', 'ik')
        else:
            self._control = self._control.replace('ik', 'fk')

    def updateGimbalVisibility(self):
        print 'hola'

    def mousePressEvent(self, event):

        self.updateState()

        super(solstice_gimbalButton, self).mousePressEvent(event)

    def postCreation(self):

        """
        This method is called after the button is addded to the picker scene
        """

        super(solstice_gimbalButton, self).postCreation()

        self.updateState()

        print 'holaaa'
        self.onOffBtn.toggleOn.connect(self.updateGimbalVisibility)
        self.onOffBtn.toggleOff.connect(self.updateGimbalVisibility)