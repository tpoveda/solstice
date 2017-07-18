#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerUtils.py
by Tomás Poveda
Utilities functions used by the picke for Solstice Short Film
______________________________________________________________________
Utility functions for Solstice Pickers
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

# Import necessary modules
import maya.cmds as cmds
import maya.mel as mel

# Import UI module of the Python Maya API
# We use this module to access to the memory pointer of the main Maya window
from maya import OpenMayaUI as OpenMayaUI
from maya.OpenMayaUI import MQtUtil

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES METHODS

def getGlobalVariable(varName):

    """
    Returns the value of a MEL global variable
    @param varName: str, name of the MEL global variable
    """

    return mel.eval("$tempVar = {0}".format(varName))

def setTool(name):

    """
    Sets the current tool (translate, rotate, scale) that is being used inside Maya viewport
    """

    contextLookup = {
        'move' : "$gMove",
        'rotate' : "$gRotate",
        'scale' : "$gSacle"
    }
    toolContext = getGlobalVariable(contextLookup[name])
    cmds.setToolTo(toolContext)

def getMayaWindow():
    mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(mayaMainWindowPtr), QMainWindow)

def getMayaAPIVersion():
    return int(cmds.about(api=True))

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES CLASSES

class Splitter(QWidget, object):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):
        super(Splitter, self).__init__()

        self.setMinimumHeight(2)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(Qt.AlignVCenter)

        firstLine = QFrame()
        firstLine.setFrameStyle(QFrame.HLine)
        self.layout().addWidget(firstLine)

        mainColor = 'rgba(%s, %s, %s, 255)' % color
        shadowColor = 'rgba(45, 45, 45, 255)'

        bottomBorder = ''
        if shadow:
            bottomBorder = 'border-bottom:1px solid %s;' % shadowColor

        styleSheet = "border:0px solid rgba(0,0,0,0); \
                      background-color: %s; \
                      max-height: 1px; \
                      %s" % (mainColor, bottomBorder)

        firstLine.setStyleSheet(styleSheet)

        if text is None:
            return

        firstLine.setMaximumWidth(5)

        font = QFont()
        font.setBold(True)

        textWidth = QFontMetrics(font)
        width = textWidth.width(text) + 6

        label = QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.layout().addWidget(label)

        secondLine = QFrame()
        secondLine.setFrameStyle(QFrame.HLine)
        secondLine.setStyleSheet(styleSheet)

        self.layout().addWidget(secondLine)
