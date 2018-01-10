#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions
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
import json
import maya.OpenMayaUI as OpenMayaUI

def _getMayaWindow():
    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QMainWindow)


def readJSON(filename):

    """
    Loads data of JSON as dict
    :param filename: str, name of the JSON file to load
    """

    data = dict()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    return data


def writeJSON(filename, data):

    """
    Writes data into JSON file
    :param filename: str, name of the JSON file to write
    :param data: str, data to write into JSON file
    """

    if not data:
        return
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)