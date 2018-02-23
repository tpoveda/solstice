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

import os

import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as OpenMayaUI

# --------------------------------------------------------------------------------------------
scriptsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts')
# --------------------------------------------------------------------------------------------

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

    """
    Returns an instance of the Maya main window
    """

    maya_main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(maya_main_window_ptr), QWidget)

def getMayaAPIVersion():

    """
    Returns the Maya version
    """

    return int(cmds.about(api=True))

def pickerUndo(fn):

    """
    Undo functionality decorator for some actions of the picker
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper

def loadScript(name):
    scriptToLoad = os.path.join(scriptsPath, name)
    if not os.path.isfile(scriptToLoad):
        cmds.error('ERROR: Impossible to load {} script'.format(name))
        return
    try:
        mel.eval('source "{}"'.format(scriptToLoad).replace('\\', '/'))
    except Exception as e:
        cmds.error('ERROR: Impossible to evaluation {} script'.format(name))
        print '-'*100
        print str(e)

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES CLASSES

class Splitter(QWidget, object):

    """
    Class to create simple splitters for the picker UI
    """

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

def getMirrorControl(ctrlName):
    oldSide = None
    newSide = None
    sidesList = ['l', 'r', 'L', 'R']
    sideFormats = []
    for side in sidesList:
        sideFormats.append('_{0}_'.format(side))
        sideFormats.append('{0}_'.format(side))
        sideFormats.append('_{0}'.format(side))
        sideFormats.append('{0}'.format(side))

    for format in sideFormats:
        if format in ctrlName:
            for side in sidesList:
                if side in format:
                    oldSide = side
                    break

    if oldSide is None:
        return

    if oldSide == 'l' or oldSide == 'L':
        newSide = 'R'
    elif newSide == 'r' or oldSide == 'R':
        newSide = 'L'

    if newSide is None:
        return

    return ctrlName.replace(oldSide, newSide)


def dock_window(pickerName, pickerTitle, charName, dialog_class):
    try:
        cmds.deleteUI(pickerName)
    except:
        pass

    main_control = cmds.workspaceControl(pickerName, ttc=["AttributeEditor", -1], iw=300, mw=True, wp='preferred', label=pickerTitle)

    control_widget = OpenMayaUI.MQtUtil.findControl(pickerName)
    control_wrap = wrapInstance(long(control_widget), QWidget)
    control_wrap.setAttribute(Qt.WA_DeleteOnClose)
    win = dialog_class(pickerName, pickerTitle, charName, control_wrap)

    cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

    return win.run()