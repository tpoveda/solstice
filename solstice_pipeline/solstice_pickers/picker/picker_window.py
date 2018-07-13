#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Picker Window
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *

import os
import weakref
from functools import partial

import maya.cmds as cmds

from solstice_gui import solstice_windows


class PickerWindow(solstice_windows.Window, object):
    def __init__(self, window_name, picker_name, picker_title, char_name, full_window=False, parent=None):
        super(PickerWindow, self).__init__(name=window_name)