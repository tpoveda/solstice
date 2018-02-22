#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_decorators.py
# by Tomas Poveda
# Utility module that contains useful decorators
# ______________________________________________________________________
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
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds

def solstice_undo(fn):

    """
    Simple undo wrapper. Use @solstice_undo above the function to wrap it.
    @param fn: function to wrap
    @return wrapped function
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper