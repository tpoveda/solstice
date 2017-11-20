#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_moduleButton.py
# by Tomás Poveda
# Custom button used to select complete modules of the rig
# ______________________________________________________________________
# Button classes for module selectors
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

class solstice_moduleButton(baseBtn.solstice_pickerBaseButton, object):
    def __init__(self,
                 x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
        super(solstice_moduleButton, self).__init__(
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
        super(solstice_moduleButton, self).setInfo(btnInfo)

        self.setRadius(btnInfo['radius'])
        self.setWidth(btnInfo['width'])
        self.setHeight(btnInfo['height'])
        self.setPart(btnInfo['part'])
        self.setSide(btnInfo['side'])
        if btnInfo['color'] != None:
            self.setInnerColor(btnInfo['color'])
        if btnInfo['glowColor'] != None:
            self.setGlowColor(btnInfo['glowColor'])

    def mousePressEvent(self, event):
        super(solstice_moduleButton, self).mousePressEvent(event)
        moduleCtrls = self._scene.getPartControls(self._part, self._side)
        mel.eval('vlRigIt_selectModuleControls("{}")'.format(moduleCtrls[0]))