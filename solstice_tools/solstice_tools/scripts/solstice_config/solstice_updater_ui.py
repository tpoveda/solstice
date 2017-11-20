try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import solstice_updater

import tempfile
import os
import re
import urllib2
import json
import time
import shutil
import zipfile

class solstice_updater_ui(QMainWindow, object):
    def __init__(self):
        super(solstice_updater_ui, self).__init__(_getMayaWindow())

        winName = "solstice_updater_ui_win"

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName, window=True)
        elif cmds.windowPref(winName, exists=True):
            cmds.windowPref(winName, remove=True)

        # Set the window object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('Solstice Tools - Updater V1.0')
        self.setFixedSize(QSize(350, 200))

        self.customUI()

        self.show()

    def customUI(self):

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        self.mainLayout = QVBoxLayout(mainWidget)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(0)
        mainWidget.setLayout(self.mainLayout)

        frameLayout = QVBoxLayout()
        mainFrame = QFrame()
        mainFrame.setFrameShape(QFrame.Box)
        mainFrame.setContentsMargins(5, 5, 5, 5)
        mainFrame.setFrameShadow(QFrame.Sunken)
        mainFrame.setLayout(frameLayout)
        self.mainLayout.addWidget(mainFrame)

        installVersionLayout = QHBoxLayout()
        self.installedVersionLbl = QLabel('Installed Version: ')
        self.versionLbl = QLabel()
        installVersionLayout.addWidget(self.installedVersionLbl)
        installVersionLayout.addWidget(self.versionLbl)

        lastVersionLayout = QHBoxLayout()
        self.lastVersionLbl = QLabel('     Latest Version: ')
        self.lastVersion = QLabel()
        lastVersionLayout.addWidget(self.lastVersionLbl)
        lastVersionLayout.addWidget(self.lastVersion)

        self.progressBar = QProgressBar()
        self.progressBarText = QLabel('=> ... <=')
        self.progressBarText.setAlignment(Qt.AlignCenter)
        self.updateBtn = QPushButton('Update')
        #self.updateBtn.setEnabled(False)

        frameLayout.addLayout(installVersionLayout)
        frameLayout.addLayout(lastVersionLayout)
        frameLayout.addWidget(divider(None))
        frameLayout.addWidget(self.progressBar)
        frameLayout.addWidget(self.progressBarText)
        frameLayout.addWidget(divider(None))
        frameLayout.addWidget(self.updateBtn)

        retrieveInfo()

        self.updateBtn.clicked.connect(solstice_updater.updateTools)

def retrieveInfo():
    pass

def _checkUI():
    pass

def divider(parent):

    """
    Create divider ui widget.
    """
    line = QFrame(parent)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line

def _getMayaWindow():

    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QMainWindow)

def initUI():
    solstice_updater_ui()
