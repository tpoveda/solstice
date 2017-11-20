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

# Import standard Python modules
from functools import partial
import os

# Import Maya command modules
import maya.cmds as cmds
import maya.mel as mel

# Import UI module of the Python Maya API
# We use this module to access to the memory pointer of the main Maya window
from maya import OpenMayaUI as OpenMayaUI

# Import modules to ensure UI dockable behavior inside Maya for our picker window
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# Import custom modules
import solstice_pickerUtils as pickerUtils

class solstice_pickerWindow(MayaQWidgetDockableMixin, QDialog):

    MAYA2014 = 201400
    MAYA2015 = 201500
    MAYA2016 = 201600
    MAYA2016_5 = 201650
    MAYA2017 = 201700

    def __init__(self, pickerName, pickerTitle, charName):

        """
        Constructor
        """

        # Before starting, we remove any instance of this window
        self._deleteInstances()

        super(solstice_pickerWindow, self).__init__(parent=pickerUtils.getMayaWindow())

        self.pickerName = pickerName
        self.pickerTitle = pickerTitle
        self.charName = charName

        cmds.select(clear=True)

        if not self.initSetup():
            self.close()
            return
        
        self._createUI()
        self.toolUI()
    
    def _createUI(self):
        
        """
        Method initializes the UI
        """

        # ===================== DOCKABLE WINDOW FUNCTIONALITY ====================== #
        mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
        self.mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QMainWindow)
        self.setObjectName(self.pickerName)                                     # This name must be unique to ensure that the tool is deleted correctly
        self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.pickerTitle)

        cmds.select(clear=True)

        self._run()

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

        # Set initial widget and layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Menu bar
        menubarWidget = QWidget()
        menubarLayout = QVBoxLayout()
        menubarWidget.setLayout(menubarLayout)
        menubar = QMenuBar()
        settingsFile = menubar.addMenu('Settings')
        exitAction = QAction('Solstice', menubarWidget)
        settingsFile.addAction(exitAction)
        exitAction.triggered.connect(self.test)
        menubarLayout.addWidget(menubar)
        self.layout().addWidget(menubarWidget)

        # Add a scrollbar
        self.scrollArea = QScrollArea()
        self.scrollArea.setFocusPolicy(Qt.NoFocus)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(self.scrollArea)

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

    def test(self):
        print 'Solstice'

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

    def dockCloseEventTriggered(self):

        """
        If the tool is in floating window mode, when the window is closed this method will be called
        """

        self._deleteInstances()

    def close(self):

        """
        Method that is called when we want to close the application and close the application
        in a way or other depending if the tool is docked or not
        """

        if self.dockWidget:
            cmds.deleteUI(self.dockName)
        else:
            QDialog.close(self)
        self.dockWidget = self.dockName = None

    def _deleteInstances(self):

        """
        Deletes any created instance of this class
        """

        def delete2016():
            # Loop through all the child elmenents of the main Maya window
            for obj in pickerUtils.getMayaWindow().children():
                if str(type(obj)) == "<class 'maya.app.general.mayaMixin.MayaQDockWidget'>":
                    # We compare the name of those elements with the name of our tool
                    if obj.widget().__class__.__name__ == self.__class__.__name__:
                        # If there is any match, we delete that instance
                        obj.setParent(None)
                        obj.deleteLater()
        
        def delete2017():
            # Loop through all the child elements of the main Maya window
            for obj in pickerUtils.getMayaWindow().children():
                if str(type(obj)) == "<class '{}.{}'>".format(os.path.splitext(os.path.basename(__file__)[0]), self.__class__.__name__):
                    if obj.__class__.__name__ == self.pickerName:
                        obj.setParent(None)
                        obj.deleteLater()

        if pickerUtils.getMayaAPIVersion() < self.__class__.MAYA2017:
            delete2016()
        else:
            delete2017()

    def _deleteControl(self, control):
        if cmds.workspaceControl(control, query=True, exists=True):
            cmds.workspaceControl(control, e=True, close=True)
            cmds.deleteUI(control, control=True)

    def _run(self):
        
        def run2016():
            self.setObjectName(self.pickerName)
            self.show(dockable=True, area='right', floating=False)
            self.raise_()
            self.setDockableParameters(width=420)
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            #self.setMinimumWidth(420)
            #self.setMaximumWidth(600)
            self.setMaximumWidth(800)

        def run2017():
            self.setObjectName(self.pickerName)
            # _deleteInstances() function does not remove the workspace control, so we have to remove it manually
            workspaceControlName = self.objectName() + 'WorkspaceControl'
            self._deleteControl(workspaceControlName)
            self.show(dockable=True, area='right', floating=False)
            cmds.workspaceControl(workspaceControlName, e=True, ttc=['AttributeEditor', -1], wp='preferred', mw=420)
            self.raise_()
            self.setDockableParameters(width=420)
            self.setMaximumWidth(800)

        if pickerUtils.getMayaAPIVersion() < self.__class__.MAYA2017:
            run2016()
        else:
            run2017()