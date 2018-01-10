#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_fkIkSwitcherButton.py
# by Tomas Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Button used to fkIk switch (all in one button)
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

import solstice_toggleButton as toggle
from .. import solstice_pickerUtils as utils

class solstice_fkIkSwitcherButton(toggle.solstice_toggleButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None, onText='ON', offText='OFF'):

        super(solstice_fkIkSwitcherButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            btnInfo=btnInfo,
            parent=parent,
            onText='IK',
            offText='FK'
        )

        self.toggleOn.connect(self.switchToIk)
        self.toggleOff.connect(self.switchToFk)

    def switchToFk(self):

        # TODO If gimbal control is selected select its fk control

        self.getPart().setFK()
        sel = cmds.ls(sl=True)
        if len(sel) > 0:
            currCtrl = sel[0]
            fkIkCtrl = self.getPart().getButtonByName(currCtrl)
            if len(fkIkCtrl) > 0:
                fkIkCtrl = fkIkCtrl[0].getFkIkControl()
                if fkIkCtrl and cmds.objExists(fkIkCtrl):
                    cmds.select(fkIkCtrl, r=True)
                    utils.setTool('rotate')

    def switchToIk(self):

        # TODO If gimbal control is selected select its ik control

        self.getPart().setIK()
        sel = cmds.ls(sl=True)
        if len(sel) > 0:
            currCtrl = sel[0]
            fkIkCtrl = self.getPart().getButtonByName(currCtrl)
            if len(fkIkCtrl) > 0:
                fkIkCtrl = fkIkCtrl[0].getFkIkControl()
                if fkIkCtrl and cmds.objExists(fkIkCtrl):
                    cmds.select(fkIkCtrl, r=True)
                    utils.setTool('move')

    def updateState(self):

        """
        Update current state of the toggle button
        """

        fkIkState = self.getPart().getFKIK(asText=True)
        if fkIkState == 'IK':
            self._pressed = True
        else:
            self.pressed = False

        print 'Updating FKIKSwitcherButtonState ...'

    def postCreation(self):

        """
        This method is called after the button is addded to the picker scene
        """

        self.updateState()
        self.getPart().fkSignal.connect(self.updateState)
        self.getPart().ikSignal.connect(self.updateState)


    def getInfo(self):

        """
        Override this to avoid problem with module selection (Check workaround for this)
        """

        return None


