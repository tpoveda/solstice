#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_winterBodyPicker.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Body Picker for Winter Character
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

from ..picker import solstice_picker as picker

class solstice_winterBodyPicker(picker.solstice_picker):
    def __init__(self, dataPath=None, imagePath=None, parent=None):
        super(solstice_winterBodyPicker, self).__init__(dataPath=dataPath, imagePath=imagePath, parent=parent)