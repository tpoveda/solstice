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


from functools import partial
import maya.cmds as cmds
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


    def setInfo(self, btnInfo):
        super(solstice_gimbalButton, self).setInfo(btnInfo)

        self.onOffPos = [btnInfo['x']+6, btnInfo['y']+17]


    def updateState(self):

        """
        Update current state of the toggle button
        """

        self.onOffBtn.move(self.onOffPos[0], self.onOffPos[1])

        parts = ['', '']
        if 'arm' in str(self.getPart().name):
            parts = ['wrist', 'arm']
        elif 'leg' in str(self.getPart().name):
            parts = ['ankle', 'foot']

        fkIkState = self.getPart().getFKIK(asText=True)
        print(self._control)
        if fkIkState == 'IK':
            if 'ik' in self._control:
                self._control = self._control.replace('ik_'+parts[0], 'ik_'+parts[1])
            else:
                self._control = self._control.replace('fk_'+parts[0], 'ik_'+parts[1])
        else:
            if 'ik' in self._control:
                self._control = self._control.replace('ik_'+parts[0], 'fk_'+parts[0])
            else:
                self._control = self._control.replace('ik_'+parts[1], 'fk_'+parts[0])

        print(self._control)


    def updateGimbalVisibility(self, isEnabled):

        self.updateState()
        ctrl = self._control.replace('_gimbalHelper', '')
        cmds.setAttr(ctrl+'.gimbalHelper', isEnabled)


    def mousePressEvent(self, event):

        self.updateState()

        super(solstice_gimbalButton, self).mousePressEvent(event)

    def postCreation(self):

        """
        This method is called after the button is addded to the picker scene
        """

        super(solstice_gimbalButton, self).postCreation()

        self.updateState()

        self.onOffBtn.toggleOn.connect(partial(self.updateGimbalVisibility, True))
        self.onOffBtn.toggleOff.connect(partial(self.updateGimbalVisibility, False))