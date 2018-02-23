#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: sPicker.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Solstice characters
______________________________________________________________________
==================================================================="""

# Import PySide modules
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
import maya.cmds as cmds
import solstice_pickerView
import solstice_pickerCommands as commands

class solstice_picker(QWidget, object):
    def __init__(self, dataPath=None, imagePath=None, parent=None):
        super(solstice_picker, self).__init__(parent=parent)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        self.view = solstice_pickerView.solstice_pickerView(dataPath=dataPath, imagePath=imagePath)
        self.mainLayout.addWidget(self.view)

        bottomLayout = QHBoxLayout()
        bottomLayout.setContentsMargins(2,2,2,2)
        bottomLayout.setSpacing(2)
        reloadBtn = QPushButton('Reload')
        updateBtn = QPushButton('Update')
        bottomLayout.addWidget(reloadBtn)
        bottomLayout.addWidget(updateBtn)
        reloadBtn.clicked.connect(self.view.scene().reloadData)
        updateBtn.clicked.connect(self.view.scene().updateState)
        self.mainLayout.addLayout(bottomLayout)

    def setNamespace(self, namespace):
        self.view.scene().setNamespace(namespace)

    def setView(self, view):
        if not view:
            return
        if self.view:
            self.view.setParent(None)
            self.view.deleteLater()
        self.view = view
        self.addWidget(self.view)

    def view(self):
        return self.view

    def addButton(self):
        self.view.scene().addButton()

    def contextMenuEvent(self, event):

        """
        Show a global scene context menu
        """

        menu = QMenu(self)
        exportPickerDataAction = menu.addAction('Export Picker Data')
        menu.addSeparator()
        selectGlobalAction = menu.addAction('Select Global Control')
        selectAllControlsAction = menu.addAction('Select All Controls')
        selectBodyControlsAction = menu.addAction('Select Body Controls')
        selectFaceControlsAction = menu.addAction('Select Face Controls')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == exportPickerDataAction:
            self._exportPickerData()
        elif action == selectGlobalAction:
            commands.selectGlobalControl()
        elif action == selectAllControlsAction:
            commands.selectAllControls()
        elif action == selectBodyControlsAction:
            commands.selectBodyControls()
        elif action == selectFaceControlsAction:
            commands.selectFaceControls()

    def mousePressEvent(self, event):
        super(solstice_picker, self).mousePressEvent(event)
        cmds.select(clear=True)

    def _exportPickerData(self):
        print 'Exporting picker data ...'
        self.view.scene().getJSONFile()

    def reloadData(self):
        self.view.scene().reloadData()

    def updateState(self):
        self.view.scene().updateScene()