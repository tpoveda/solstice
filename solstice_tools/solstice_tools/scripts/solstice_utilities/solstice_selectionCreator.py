#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_selectionCreator.py
# by Tomas Poveda
# Tool used by TDs to create selection sets for different purposes
# ______________________________________________________________________# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import os
import json
from functools import partial

import maya.cmds as cmds

from solstice_decorators import solstice_undo
from solstice_utils import _getMayaWindow, readJSON
from solstice_gui import solstice_splitters
from solstice_libs import solstice_naming

class solstice_selectionCreator(QMainWindow, object):
    def __init__(self):
        super(solstice_selectionCreator, self).__init__(_getMayaWindow())

        winName = 'solstice_selectionCreator_window'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('Solstice Tools - Selections Creator - v.1.0')
        self.customUI()
        self.show()

    def customUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignCenter)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        selectionTypeLbl = QLabel('Selection Type')
        selectionTypeLbl.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(selectionTypeLbl)
        mainLayout.addLayout(solstice_splitters.SplitterLayout())

        self.gridLayout = QGridLayout()
        mainLayout.addLayout(self.gridLayout)

        self._updateSelections()

    def _updateSelections(self):
        self._selections_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solstice_selections.json')
        if not os.path.isfile(self._selections_file):
            msgBox = QMessageBox()
            msgBox.setText('Selection File does not exists. Contact Solstice TD team!')
            msgBox.exec_()
            return

        selections = readJSON(self._selections_file)['selections']
        row = 0
        column = 0
        for i, sel in enumerate(selections):
            if column > 1:
                column = 0
            btn = QPushButton(sel.get('name'))
            btn.clicked.connect(partial(self.createSelection, sel.get('type')))
            self.gridLayout.addWidget(btn, row, column)
            column += 1
            if (i + 1) % 2 == 0:
                row += 1

    @solstice_undo
    def createSelection(self, type, selFilter='transform'):

        if not type:
            cmds.confirmDialog(title='Error', message='Selection type {} is not valid. Please contact TD team!'.format(type))
            return None

        fullSel = cmds.ls(sl=True, l=True)
        if not fullSel:
            cmds.confirmDialog(title='Error', message='Selection cannot be empty, select Maya nodes first and try again!')
            return None

        sel = fullSel[0]
        name = '{}_{}_abc'.format(solstice_naming.getName(sel), type)

        if cmds.objExists(name):
            res = cmds.confirmDialog(title='Selection Exists!', message='Do you want to overwrite existing selection?', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            if not res or res != 'Yes':
                pass
            else:
                cmds.delete(name)

        objs = cmds.listRelatives(fullSel, ad=True, f=True) or []
        mainSel = list()
        for obj in objs:
            p = cmds.listRelatives(obj, parent=True, f=True)
            p = p[0] if p else None
            if p and p in objs:
                continue
            mainSel.append(obj)

        if selFilter:
            sel = filter(lambda x: cmds.objectType(x, isType=selFilter), mainSel)

        return cmds.sets(sel, n=name)

def initUI():
    solstice_selectionCreator()