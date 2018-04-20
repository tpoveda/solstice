#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_color.py
# by Tomas Poveda
# Module that defines that extends QColor functionality
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtGui import *

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
