#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_texturesRelinker.py
# by Tomas Poveda
# Tool used by textures artists to relink textures path
# ______________________________________________________________________
# ==================================================================="""

import os

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.cmds as cmds

from solstice_decorators import solstice_undo
from solstice_utils import _getMayaWindow

# -------------------------------------------------------------------------------------------------

class solstice_texturesRelinker(QMainWindow, object):
    def __init__(self):
        super(solstice_texturesRelinker, self).__init__(_getMayaWindow())

        winName = 'solstice_texturesRelinker_window'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('Solstice Tools - Textures Relinker - v1.1')
        #self.setFixedSize(QSize(1200, 780))

        self.customUI()

        self.artellaVar = os.environ.get('ART_LOCAL_ROOT')
        self.solsticeProject = os.environ.get('SOLSTICE_PROJECT')

        if self.artellaVar is None or self.solsticeProject is None:
            msgBox = QMessageBox()
            msgBox.setText('Solstice environment variables are not setup correctly! Make sure you have Solstice Tools intalled and restart Maya!')
            msgBox.exec_()
            return

        self.show()

    def customUI(self):

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(2)
        mainLayout.setAlignment(Qt.AlignTop)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        pathsLayout = QVBoxLayout()
        pathsLayout.setContentsMargins(5,5,5,5)
        pathsLayout.setSpacing(2)
        mainLayout.addLayout(pathsLayout)

        targetLayout = QHBoxLayout()
        targetLayout.setContentsMargins(5,5,5,5)
        targetLayout.setSpacing(2)
        pathsLayout.addLayout(targetLayout)
        newTxtLbl = QLabel('     Artella Asset Textures Folder Path: ')
        self.newTxtLine = QLineEdit()
        newTxtBtn = QPushButton('...')
        newTxtBtn.setMaximumWidth(30)
        for widget in [newTxtLbl, self.newTxtLine, newTxtBtn]:
            targetLayout.addWidget(widget)

        checkTexturesBtn = QPushButton('Check Textures Path')
        mainLayout.addWidget(checkTexturesBtn)

        listsLayout = QHBoxLayout()
        listsLayout.setContentsMargins(5,5,5,5)
        listsLayout.setSpacing(2)
        currListLayout = QVBoxLayout()
        currListLayout.setContentsMargins(5,5,5,5)
        currListLayout.setSpacing(2)
        newListLayout = QVBoxLayout()
        newListLayout.setContentsMargins(5,5,5,5)
        newListLayout.setSpacing(2)
        listsLayout.addLayout(currListLayout)
        listsLayout.addLayout(newListLayout)
        mainLayout.addLayout(listsLayout)

        currListsLayout = QHBoxLayout()
        currListsLayout.setContentsMargins(5,5,5,5)
        currListsLayout.setSpacing(2)
        bottomCurrListLayout = QHBoxLayout()
        bottomCurrListLayout.setContentsMargins(5,5,5,5)
        bottomCurrListLayout.setSpacing(2)
        currListLayout.addLayout(currListsLayout)
        currListLayout.addLayout(bottomCurrListLayout)
        self.totalCurrTxtLbl = QLabel()
        self.totalCurrTxtLbl.setAlignment(Qt.AlignCenter)
        currAssetTexturesPathListLayout = QVBoxLayout()
        currAssetTexturesPathListLayout.setContentsMargins(5,5,5,5)
        currAssetTexturesPathListLayout.setSpacing(2)
        currListsLayout.addLayout(currAssetTexturesPathListLayout)
        currAssetTexturesPathListLbl = QLabel('File Name')
        currAssetTexturesPathListLbl.setAlignment(Qt.AlignCenter)
        self.currAssetTexturesPathListNames = QListWidget()
        self.currAssetTexturesPathListNames.setMaximumWidth(200)
        
        currAssetTexturesPathLayout = QVBoxLayout()
        currAssetTexturesPathLayout.setContentsMargins(5,5,5,5)
        currAssetTexturesPathLayout.setSpacing(2)
        currListsLayout.addLayout(currAssetTexturesPathLayout)

        currAssetTexturesPathLbl = QLabel('Texture Path')
        currAssetTexturesPathLbl.setAlignment(Qt.AlignCenter)
        self.currAssetTexturesPathList = QListWidget()

        self.currTexturesPathUpdateBtn = QPushButton('Update')

        currAssetTexturesPathListLayout.addWidget(currAssetTexturesPathListLbl)
        currAssetTexturesPathListLayout.addWidget(self.currAssetTexturesPathListNames)

        currAssetTexturesPathLayout.addWidget(currAssetTexturesPathLbl)
        currAssetTexturesPathLayout.addWidget(self.currAssetTexturesPathList)
        bottomCurrListLayout.addWidget(self.currTexturesPathUpdateBtn)
        bottomCurrListLayout.addWidget(self.totalCurrTxtLbl)

        newListsLayout = QHBoxLayout()
        newListsLayout.setContentsMargins(5,5,5,5)
        newListsLayout.setSpacing(2)
        bottomNewListLayout = QHBoxLayout()
        bottomNewListLayout.setContentsMargins(5,5,5,5)
        bottomNewListLayout.setSpacing(2)
        newListLayout.addLayout(newListsLayout)
        newListLayout.addLayout(bottomNewListLayout)
        self.totalNewTxtLbl = QLabel()
        self.totalNewTxtLbl.setAlignment(Qt.AlignCenter)

        newTexturesPathListLayout = QVBoxLayout()
        newTexturesPathListLayout.setContentsMargins(5,5,5,5)
        newTexturesPathListLayout.setSpacing(2)
        newListsLayout.addLayout(newTexturesPathListLayout)
        newTexturesPathListLbl = QLabel('Valid Relinking Paths')
        newTexturesPathListLbl.setAlignment(Qt.AlignCenter)
        self.newTexturesPathList = QListWidget()

        newTexturesNoValidPathListLayout = QVBoxLayout()
        newTexturesNoValidPathListLayout.setContentsMargins(5,5,5,5)
        newTexturesNoValidPathListLayout.setSpacing(2)
        newListsLayout.addLayout(newTexturesNoValidPathListLayout)
        newTexturesNoValidPathListLbl = QLabel('No Valid Relinking Paths')
        newTexturesNoValidPathListLbl.setAlignment(Qt.AlignCenter)
        self.newNoValidTexturesPathList = QListWidget()
        self.newTexturesPathUpdateBtn = QPushButton('Update')

        newTexturesPathListLayout.addWidget(newTexturesPathListLbl)
        newTexturesPathListLayout.addWidget(self.newTexturesPathList)

        newTexturesNoValidPathListLayout.addWidget(newTexturesNoValidPathListLbl)
        newTexturesNoValidPathListLayout.addWidget(self.newNoValidTexturesPathList)
        bottomNewListLayout.addWidget(self.totalNewTxtLbl)
        bottomNewListLayout.addWidget(self.newTexturesPathUpdateBtn)

        relinkTexturesBtn = QPushButton('Relink Textures')
        mainLayout.addWidget(relinkTexturesBtn)

        self.statusBar().showMessage('Solstice Tools - Textures Relinker - V1.0')

        menubar = self.menuBar()
        helpMenu = menubar.addMenu('&Help')

        # === SIGNALS === #

        checkTexturesBtn.clicked.connect(self._checkNewTextures)
        newTxtBtn.clicked.connect(self._setTexturesPath)
        relinkTexturesBtn.clicked.connect(self._relinkTextures)

        # ------------------------------------------------------------

        self.relinkingList = {}

        self._checkAssetTextures()

    def _setTexturesPath(self):
        selDir = QFileDialog.getExistingDirectory()
        if os.path.exists(selDir):
            self.newTxtLine.setText(selDir)

    def _checkNewTextures(self):

        if self.newTxtLine.text() != '' and os.path.exists(self.newTxtLine.text()):
            files = [os.path.join(self.newTxtLine.text(),f) for f in os.listdir(self.newTxtLine.text())]
            filesPath = list()
            currScenesTxts = list()
            for index in xrange(self.currAssetTexturesPathList.count()):
                filePath = self.currAssetTexturesPathList.item(index).text()
                basePath = os.path.basename(filePath)
                currScenesTxts.append(os.path.splitext(basePath)[0])
            
            renamedItems = 0

            for i,f in enumerate(files):

                newPath = f.replace(self.solsticeProject, '$SOLSTICE_PROJECT/')
                baseFile = os.path.basename(f)
                fileName = os.path.splitext(baseFile)[0]

                if newPath not in filesPath:
                    filesPath.append(newPath)

                item = QListWidgetItem(newPath)

                if fileName in currScenesTxts:
                    item.setBackground(Qt.green)
                    item.setForeground(Qt.black)
                    self.relinkingList[fileName] = newPath
                    renamedItems += 1
                    self.newTexturesPathList.addItem(item)
                else:
                    self.newNoValidTexturesPathList.addItem(item)

            self.totalNewTxtLbl.setText('Found ' + str(renamedItems) + ' textures to relink!')

    def _checkAssetTextures(self):

        files = cmds.ls(type='file')
        filesPath = list()

        for f in files:
            fPath = cmds.getAttr(f+'.fileTextureName')
            dirPath = os.path.split(fPath)[0]

            if dirPath not in filesPath:
                filesPath.append(dirPath)

            itemName = QListWidgetItem(f)
            item = QListWidgetItem(fPath)
            if 'S_PRP_' not in f:
                itemName.setBackground(Qt.yellow)
                itemName.setForeground(Qt.black)
            self.currAssetTexturesPathListNames.addItem(itemName)
            self.currAssetTexturesPathList.addItem(item)
        
        self.totalCurrTxtLbl.setText('Found ' + str(len(files)) + ' files in the asset scene!')

    @solstice_undo
    def _relinkTextures(self):
        print ' ========= RELINKING TEXTURES ========='
        files = cmds.ls(type='file')
        if self.newTexturesPathList.count() > 0 and len(self.relinkingList.items()) > 0:
            for fileName, filePath in self.relinkingList.iteritems():
                for i in xrange(self.currAssetTexturesPathList.count()):
                    if fileName in self.currAssetTexturesPathList.item(i).text():
                        for f in files:
                            if cmds.getAttr(f+'.fileTextureName') == self.currAssetTexturesPathList.item(i).text():
                                print 'Relinking texture {} to {}'.format(self.currAssetTexturesPathList.item(i).text(), filePath)
                                cmds.setAttr(f+'.fileTextureName', filePath, type='string')

def initUI():
    solstice_texturesRelinker()

