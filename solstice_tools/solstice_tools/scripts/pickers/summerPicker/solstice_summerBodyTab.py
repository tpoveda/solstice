#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_summerBodyTab.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Body Picker Tab for Summer Character
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
import os

# Import custom modules
from ..picker import solstice_pickerTab as pickerTab

imagesPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')

class solstice_summerBodyTab(pickerTab.solstice_pickerTab, object):
    def __init__(self, name, parent=None):
        super(solstice_summerBodyTab, self).__init__(parent)

        self.name = name

        self.setBackgroundImage(os.path.join(imagesPath, 'pickerSummer_body.png'))