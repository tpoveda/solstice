#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Customized picker for Summer Character
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os

from solstice.pipeline.tools.pickers.picker import utils as utils
from solstice.pipeline.tools.pickers.picker import pickerwindow


class SummerPicker(pickerwindow.PickerWindow, object):

    name = 'Summer Picker'
    title = 'Solstice Tools - Summer Picker'
    version = '1.0'
    docked = True

    def __init__(self, picker_name, picker_title, char_name, parent=None, full_window=False):

        picker_images_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
        picker_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

        super(SummerPicker, self).__init__(
            picker_name=picker_name,
            picker_title=picker_title,
            char_name=char_name,
            data_path=picker_data_path,
            images_path=picker_images_path,
            parent=parent,
            full_window=full_window)


def run(full_window=True):
    utils.dock_window(picker_name='summer_picker', picker_title='Solstice - Summer Picker', character_name='Summer', dialog_class=SummerPicker)
