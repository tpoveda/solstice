#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_picker.py
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

from functools import partial
import os
import weakref

import maya.cmds as cmds
import maya.mel as mel
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import solstice_pickerUtils as pickerUtils

# Global variable that stores current opened picker
global window_picker


class Solstice_PickerWindow(QWidget, object):

    instances = list()

    def __init__(self, pickerName, pickerTitle, charName, parent=None):

        """
        Constructor
        """

        super(Solstice_PickerWindow, self).__init__(parent)

        Solstice_PickerWindow._deleteInstances()
        self.__class__.instances.append(weakref.proxy(self))
        self.pickerTitle = pickerTitle

        self.window_name = pickerName
        self.ui = parent

        self.charName = charName

        if not self.initSetup():
            self.close()
            return

        cmds.select(clear=True)

        self.toolUI()

        global window_picker
        window_picker = self


    def initSetup(self):

        if not os.path.exists(pickerUtils.scriptsPath):
            cmds.error('ERROR: Summer Scripts do not found!')
            return

        # Load scripts in the correct order
        pickerUtils.loadScript('vlRigIt_getModuleFromControl.mel')
        pickerUtils.loadScript('vlRigIt_getControlsFromModuleList.mel')
        pickerUtils.loadScript('vlRigIt_selectModuleControls.mel')
        pickerUtils.loadScript('vlRigIt_snap_ikFk.mel')
        pickerUtils.loadScript('vl_resetTransformations.mel')
        pickerUtils.loadScript('vl_resetAttributes.mel')
        pickerUtils.loadScript('vl_contextualMenuBuilder.mel')


    def toolUI(self):

        """
        Function where all the UI of the picker is loaded
        """

        # Menu bar
        menubarWidget = QWidget()
        menubarLayout = QVBoxLayout()
        menubarWidget.setLayout(menubarLayout)
        menubar = QMenuBar()
        settingsFile = menubar.addMenu('Settings')
        exitAction = QAction('Solstice', menubarWidget)
        settingsFile.addAction(exitAction)
        # exitAction.triggered.connect(self.test)
        menubarLayout.addWidget(menubar)
        self.parent().layout().addWidget(menubarWidget)

        # Add a scrollbar
        self.scrollArea = QScrollArea()
        self.scrollArea.setFocusPolicy(Qt.NoFocus)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.parent().layout().addWidget(self.scrollArea)

        # Add main tab
        self._mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(5, 25, 5, 5)
        self.mainLayout.setAlignment(Qt.AlignTop)
        self._mainWidget.setLayout(self.mainLayout)
        self.scrollArea.setWidget(self._mainWidget)

        namespaceLayout = QHBoxLayout()
        namespaceLayout.setContentsMargins(5, 5, 5, 5)
        namespaceLayout.setSpacing(2)
        namespaceLbl = QLabel('Charater namespace: ')
        namespaceLbl.setMaximumWidth(115)
        self.namespace = QComboBox()
        namespaceLayout.addWidget(namespaceLbl)
        namespaceLayout.addWidget(self.namespace)
        self.mainLayout.addLayout(namespaceLayout)

        # Add character image
        self._charLbl = QLabel()
        self._charLbl.setAlignment(Qt.AlignCenter)
        #self.mainLayout.addWidget(self._charLbl)

        # Add character text label
        self._charTxtLbl = QLabel(self.charName)
        self._charTxtLbl.setAlignment(Qt.AlignCenter)
        #self.mainLayout.addWidget(self._charTxtLbl)

        self.updateNamespaces()

    def updateNamespaces(self):
        currNamespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for ns in currNamespaces:
            if ns not in ['UI', 'shared']:
                self.namespace.addItem(ns)
        self.namespace.setCurrentIndex(0)

    def setCharacterText(self, text):

        """
        Sets the text of the picker text
        """

        self._charTxtLbl.setText(text)

    def setCharacterImage(self, imagePath):

        """
        Sets the character image
        """

        if os.path.isfile(imagePath):
            charPixmap = QPixmap(imagePath)
            self._charLbl.setPixmap(charPixmap.scaled(100,100, Qt.KeepAspectRatio))

    @staticmethod
    def _deleteInstances():
        for ins in Solstice_PickerWindow.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
            except:
                # Ignore the fact that the actual parent has already been deleted by Maya ...
                pass

            Solstice_PickerWindow.instances.remove(ins)
            del ins

    def run(self):
        return self