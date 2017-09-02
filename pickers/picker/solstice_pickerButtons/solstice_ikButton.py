#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_ikButton.py
# by Tomás Poveda
# Custom button used by the picker of Solstice Short Film
# ______________________________________________________________________
# Button classes for IK picker buttons
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

class solstice_ikButton(baseBtn.solstice_pickerBaseButton, object):
    def __init__(
            self, x=0, y=0, text='', control='', parentCtrl='', radius=30, btnInfo=None, parent=None):

        btnText = text
        if text == '' or text == None:
            btnText = 'IK'

        super(solstice_ikButton, self).__init__(
            x=x,
            y=y,
            text=btnText,
            control=control,
            parentCtrl=parentCtrl,
            radius=radius,
            innerColor=colors.yellow,
            btnInfo=btnInfo,
            parent=parent)

    def setInfo(self, btnInfo):
        super(solstice_ikButton, self).setInfo(btnInfo)

        self.setControl(btnInfo['control'])
        self.setParentControl(btnInfo['parent'])
        self.setRadius(btnInfo['radius'])
        self.setGizmo(btnInfo['gizmo'])

    def contextMenuEvent(self, event):
        menu = QMenu()
        selectHierarchyAction = menu.addAction('Select Hierarchy')
        resetControlAction = menu.addAction('Reset Control')
        mirrorControlAction = menu.addAction('Mirror Control')
        flipControlAction = menu.addAction('Flip Control')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == selectHierarchyAction:
            self._selectHierarchy()
        elif action == resetControlAction:
            self._resetControl()
        elif action == mirrorControlAction:
            self._mirrorControl()
        elif action == flipControlAction:
            self._flipControl()