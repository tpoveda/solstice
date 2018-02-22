#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_extraButton.py
# by Tomás Poveda
# Custom button used to select complete modules of the rig
# ______________________________________________________________________
# Button classes for extra controls
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
import maya.mel as mel

from .. import solstice_pickerColors as colors
from .. import solstice_pickerBaseButton as baseBtn

class solstice_extraButton(baseBtn.solstice_pickerBaseButton, object):
    def __init__(self,
                 x=0, y=0, text='', control='', parentCtrl='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
        super(solstice_extraButton, self).__init__(
            x=x,
            y=y,
            text=text,
            control=control,
            radius=cornerRadius,
            width=width,
            height=height,
            innerColor=colors.black,
            btnInfo=btnInfo,
            parent=parent,
            buttonShape=baseBtn.solstice_pickerButtonShape.roundedSquare
        )

    def setInfo(self, btnInfo):
        super(solstice_extraButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])
        self.setRadius(btnInfo['radius'])
        self.setGizmo(btnInfo['gizmo'])
        self.setPart(btnInfo['part'])
        self.setSide(btnInfo['side'])
        if btnInfo['color'] != None:
            self.setInnerColor(btnInfo['color'])
        if btnInfo['glowColor'] != None:
            self.setGlowColor(btnInfo['glowColor'])

    def contextMenuEvent(self, event):
        menu = QMenu()
        selectHierarchyAction = menu.addAction('Select Hierarchy')
        resetControlAction = menu.addAction('Reset Control')
        mirrorControlAction = menu.addAction('Mirror Control')
        flipControlAction = menu.addAction('Flip Control')
        resetControlAttributes = menu.addAction('Reset Control Attributes')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == selectHierarchyAction:
            self._selectHierarchy()
        elif action == resetControlAction:
            self._resetControl()
        elif action == mirrorControlAction:
            self._mirrorControl()
        elif action == flipControlAction:
            self._flipControl()
        elif action == resetControlAttributes:
            self._resetControlAtributes()