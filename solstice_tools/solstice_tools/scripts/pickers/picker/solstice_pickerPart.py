#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerPart.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Base class for picker parts
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
import maya.mel as mel

from solstice_pickerButtons import solstice_ikButton
from solstice_pickerButtons import solstice_fkButton

class solstice_pickerPart(QObject, object):

    fkSignal = Signal()
    ikSignal = Signal()

    def __init__(self, name, side):
        super(solstice_pickerPart, self).__init__()
        self._name = name
        self._side = side
        self._buttons = list()

    @property
    def name(self):
        return self._name

    @property
    def side(self):
        return self._side

    def hasFKIK(self):
        ctrlGrp = self.getControlGroup()
        if cmds.objExists(ctrlGrp):
            return cmds.attributeQuery('FK_IK', node=ctrlGrp, exists=True)
        return False

    def getFKIK(self, asText=False):
        if not self.hasFKIK():
            return None
        fkIkValue =cmds.getAttr(self.getControls()[0].controlGroup+'.FK_IK')
        if asText:
            if fkIkValue == 0:
                return 'FK'
            else:
                return 'IK'
        else:
            return fkIkValue

    def setFK(self):
        if self.hasFKIK():
            mel.eval('vlRigIt_snap_ikFk("{}","{}")'.format(self.getControlGroup(), 0))
            [btn.setVisible(False) for btn in self.getIKButtons()]
            [btn.setVisible(True) for btn in self.getFKButtons()]
            print 'Setting fk ....'
            self.fkSignal.emit()

    def setIK(self):
        if self.hasFKIK():
            mel.eval('vlRigIt_snap_ikFk("{}","{}")'.format(self.getControlGroup(), 1))
            [btn.setVisible(False) for btn in self.getFKButtons()]
            [btn.setVisible(True) for btn in self.getIKButtons()]
            print 'Setting ik .....'
            self.ikSignal.emit()

    def getControlGroup(self):
        return self.getControls()[0].controlGroup

    def getControls(self, asButtons=True):
        if asButtons:
            return self._buttons
        else:
            return [btn._control for btn in self._buttons]

    def getIKButtons(self):
        return [btn for btn in self._buttons if isinstance(btn, solstice_ikButton.solstice_ikButton)]

    def getFKButtons(self):
        return [btn for btn in self._buttons if isinstance(btn, solstice_fkButton.solstice_fkButton)]

    def addButton(self, newBtn):
        self._buttons.append(newBtn)

    def getButtonByName(self, btnName):
        return [btn for btn in self._buttons if btn._control == btnName]