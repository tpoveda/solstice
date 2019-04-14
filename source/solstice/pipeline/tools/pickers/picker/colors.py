#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Custom colors used in pickers and buttons
# ==================================================================="""

from pipeline.externals.solstice_qt.QtGui import *

black = QColor(50, 50, 50, 255)
white = QColor(255, 255, 255, 200)
red = QColor(255, 0, 0, 255)
green = QColor(0, 255, 0, 255)
blue = QColor(0, 0, 255, 255)
yellow = QColor(255, 255, 0, 255)
darkYellow = QColor(135, 135, 45)
orange = QColor(255, 150, 0)

def get_color_from_list(colors_list):
    """
    Converts list to RGB QColor
    :param colors_list: list<int>
    :return: QColor
    """

    return QColor.fromRgb(colors_list[0], colors_list[1], colors_list[2])
