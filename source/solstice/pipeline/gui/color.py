#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that defines that extends QColor functionality
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *


class Color(QColor, object):
    def __eq__(self, other):
        if other == self:
            return True
        elif isinstance(other, Color):
            return self.to_string() == other.to_string()
        else:
            return False

    @classmethod
    def from_color(cls, color):
        """
        Gets a string formateed color from a QColor
        :param color: QColor, color to parse
        :return: (str)
        """

        color = ('rgb(%d, %d, %d, %d)' % color.getRgb())
        return cls.from_string(color)

    @classmethod
    def from_string(cls, text_color):
        """
        Returns a (int, int, int, int) format color from a string format color
        :param text_color: str, string format color to parse
        :return: (int, int, int, int)
        """

        a = 255
        try:
            r, g, b, a = text_color.replace('rgb(', '').replace(')', '').split(',')
        except ValueError:
            r, g, b = text_color.replace('rgb(', '').replace(')', '').split(',')

        return cls(int(r), int(g), int(b), int(a))

    def to_string(self):
        """
        Returns the color with string format
        :return: str
        """

        return 'rgb(%d, %d, %d, %d)' % self.getRgb()

    def is_dark(self):
        """
        Return True if the color is considered dark (RGB < 125(mid grey)) or False otherwise
        :return: bool
        """

        return self.red() < 125 and self.green() < 125 and self.blue() < 125


class ColorPicker(QPushButton, object):
    """
    Custom color picker button to store and retrieve color values
    """

    valueChanged = Signal()

    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)

        self._color = None
        self.color = [1, 1, 1]

        self.clicked.connect(self._on_show_color_dialog)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, values):
        self._color = values
        self.valueChanged.emit()

        values = [int(x*255) for x in values]
        self.setStyleSheet('background: rgb({},{},{})'.format(*values))

    def _on_show_color_dialog(self):
        """
        Internal function used to display a color picker to change color
        """

        current = QColor()
        current.setRgbF(*self._color)
        colors = QColorDialog.getColor(current)
        if not colors:
            return
        self.color = [colors.redF(), colors.greenF(), colors.blueF()]
