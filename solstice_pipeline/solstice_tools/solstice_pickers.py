#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_scatter.py
# by Tomas Poveda
# Tool that allows to select the picker you want to open
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_gui import solstice_windows


class SolsticePickers(solstice_windows.Window, object):

    name = 'Picker'
    title = 'Solstice Tools - Picker Tool'
    version = '1.0'
    docked = False

    def __init__(self, name='PickersWindow', parent=None, **kwargs):
        super(SolsticePickers, self).__init__(name=name, parent=parent)

    def custom_ui(self):
        super(SolsticePickers, self).custom_ui()