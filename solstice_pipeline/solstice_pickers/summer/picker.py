#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Customized picker for Summer Character
# ==================================================================="""

import os

from Qt.QtCore import *
from Qt.QtWidgets import *

from solstice_pickers.picker import picker_window

# --------------------------------------------------------------------------------------------
images_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
# --------------------------------------------------------------------------------------------


class SummerPicker(picker_window.PickerWindow, object):

    name = 'Summer Picker'
    title = 'Solstice Tools - Summer Picker'
    version = '1.0'
    docked = True

    def __init__(self, picker_name, picker_title, char_name, full_window=False, parent=None):

        self._full_window = full_window
        self._body_picker_data = os.path.join(data_path, 'summer_body_picker_data.json')
        self._facial_picker_data = os.path.join(data_path, 'summer_facial_picker_data.json')

        super(SummerPicker, self).__init__(window_name='SummerPickerWindow', picker_name=picker_name, picker_title=picker_title, char_name=char_name, parent=parent)