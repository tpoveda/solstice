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
import maya.mel as mel
import solstice_updater

import threading
import urllib2
import tempfile
import os
import json
import time

from solstice_config import solstice_update_utils as utils

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

        self.changelog_btn = QPushButton('Changelog')
        self.changelog_btn.setMaximumWidth(60)

        frameLayout.addLayout(installVersionLayout)
        frameLayout.addLayout(lastVersionLayout)
        frameLayout.addWidget(divider(None))
        frameLayout.addWidget(self.progress_text)
        frameLayout.addWidget(divider(None))

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(2,2,2,2)
        bottom_layout.setSpacing(2)
        frameLayout.addLayout(bottom_layout)

        bottom_layout.addWidget(self.updateBtn)
        bottom_layout.addWidget(self.changelog_btn)

        self.updateBtn.clicked.connect(self._update)
        self.changelog_btn.clicked.connect(show_changelog)

        self._check_versions()

    def _check_versions(self):
        last_version, installed_version = utils.updateTools(get_versions=True)

        if installed_version:
            self.versionLbl.setText(str(installed_version))
        else:
            self.versionLbl.setText('Not installed')

        if last_version:
            self.lastVersion.setText(str(last_version))

        last_version_value = utils.getVersion(last_version)

        if last_version and installed_version:
            installed_version_value = utils.getVersion(installed_version)
            if last_version_value > installed_version_value:
                self.progress_text.setText('NEW VERSION AVAILABLE!')
                self.updateBtn.setEnabled(True)
                self.changelog_btn.setEnabled(True)
            else:
                self.progress_text.setText('SOLSTICE TOOLS ARE UP-TO-DATE!')
                self.updateBtn.setEnabled(False)
                self.changelog_btn.setEnabled(True)
        else:
            self.progress_text.setText('SOLSTICE TOOLS ARE NOT INSTALLED!')
            self.updateBtn.setEnabled(True)
            self.changelog_btn.setEnabled(False)

        changelog_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'changelog.txt')
        if not os.path.isfile(changelog_file_path):
            self.changelog_btn.setEnabled(False)

    def _update(self):
        self.close()
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        cmds.progressBar(gMainProgressBar, edit=True, beginProgress=True, isInterruptable=False, status='Downloading Solstice Tools ...', maxValue=100)
        solstice_updater.updateTools(progress_bar=gMainProgressBar)
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        # self._check_versions()

def show_changelog():

    changelog_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'changelog.txt')
    if not os.path.isfile(changelog_file_path):
        print(utils.sLog('Changelog file not found!'))
        return

    changelog_file = QFile(changelog_file_path)
    line = ''
    if changelog_file.open(QIODevice.ReadOnly | QIODevice.Text):
        file_stream = QTextStream(changelog_file)
        while not file_stream.atEnd():
            line = line + file_stream.readLine() + '\n'

    changelog_win = QMessageBox()
    changelog_win.setWindowTitle('Solstice Tools - Changelog')
    changelog_win.setText(line)
    changelog_win.exec_()


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
