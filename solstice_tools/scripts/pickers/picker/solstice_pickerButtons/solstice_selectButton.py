#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_selectButton.py
by Tomás Poveda
Custom button used by the picker of Solstice Short Film
______________________________________________________________________
Base class to be used in buttons used to select controls
______________________________________________________________________
==================================================================="""

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
from .. import solstice_pickerUtils as utils

class solstice_selectButton(baseBtn.solstice_pickerBaseButton, object):
    def __init__(self,
                 x=0, y=0, text='', cornerRadius=5, width=30, height=15, btnInfo=None, parent=None):
        super(solstice_selectButton, self).__init__(
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
        super(solstice_selectButton, self).setInfo(btnInfo)

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
        super(solstice_selectButton, self).mousePressEvent(event)
        print self.control