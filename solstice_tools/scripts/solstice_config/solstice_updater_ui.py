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

import threading
import urllib2
import tempfile
import os
import json
import time

from solstice_tools.scripts.solstice_config import solstice_update_utils as utils


class solstice_updater_ui(QDialog, object):
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

        self.exec_()

    def customUI(self):

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

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

        self.progress_text = QLabel('')
        self.progress_text.setAlignment(Qt.AlignCenter)
        self.updateBtn = QPushButton('Update')
        #self.updateBtn.setEnabled(False)

        frameLayout.addLayout(installVersionLayout)
        frameLayout.addLayout(lastVersionLayout)
        frameLayout.addWidget(divider(None))
        frameLayout.addWidget(self.progress_text)
        frameLayout.addWidget(divider(None))
        frameLayout.addWidget(self.updateBtn)

        self.updateBtn.clicked.connect(self._update)

        self._check_versions()

    def _check_versions(self):
        last_version, installed_version = utils.updateTools(get_versions=True)
        if last_version and installed_version:
            print(last_version)
            print(installed_version)
            self.versionLbl.setText(str(installed_version))
            self.lastVersion.setText(str(last_version))

            last_version_value = utils.getVersion(last_version)
            installed_version_value = utils.getVersion(installed_version)
            if last_version_value > installed_version_value:
                self.progress_text.setText('NEW VERSION AVAILABLE!')
                self.updateBtn.setEnabled(True)
            else:
                self.progress_text.setText('SOLSTICE TOOLS ARE UP-TO-DATE!')
                self.updateBtn.setEnabled(False)
        else:
            self.progress_text.setText('Solstice tools installed succesfully!')

    def _update(self):
        self.close()
        solstice_updater.updateTools()
        # self._check_versions()


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
    return solstice_updater_ui()
