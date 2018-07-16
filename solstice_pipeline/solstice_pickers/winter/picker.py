#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Customized picker for Winter Character
# ==================================================================="""

import os

from solstice_pipeline.solstice_pickers.picker import picker_utils as utils
from solstice_pipeline.solstice_pickers.picker import picker_window


class WinterPicker(picker_window.PickerWindow, object):

    name = 'Winter Picker'
    title = 'Solstice Tools - Winter Picker'
    version = '1.0'
    docked = True

    def __init__(self, picker_name, picker_title, char_name, parent=None, full_window=False):

        picker_images_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
        picker_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

        super(WinterPicker, self).__init__(
            picker_name=picker_name,
            picker_title=picker_title,
            char_name=char_name,
            data_path=picker_data_path,
            images_path=picker_images_path,
            parent=parent,
            full_window=full_window)


def run(full_window=True):
    utils.dock_window(picker_name='winter_picker', picker_title='Solstice - Winter Picker', character_name='Winter', dialog_class=WinterPicker)
