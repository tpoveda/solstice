#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class for Solstice Icons
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtGui import *
from Qt.QtCore import *

from solstice.pipeline.gui import color


class Icon(QIcon, object):
    def __init__(self, *args):
        super(Icon, self).__init__(*args)

        self._color = None

    def set_color(self, new_color, size=None):
        """
        Sets icon color
        :param new_color: QColor, new color for the icon
        :param size: QSize, size of the icon
        """

        if isinstance(new_color, str):
            new_color = color.Color.from_string(new_color)

        icon = self
        size = size or icon.actualSize(QSize(256, 256))
        pixmap = icon.pixmap(size)

        if not self.isNull():
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.setBrush(new_color)
            painter.setPen(new_color)
            painter.drawRect(pixmap.rect())
            painter.end()

        icon = QIcon(pixmap)
        self.swap(icon)

    def set_badge(self, x, y, w, h, color=None):
        """
        Adds a badge image to the icon
        :param x: int
        :param y: int
        :param w: int
        :param h: int
        :param color: QColor or None
        """

        color = color or QColor(240, 100, 100)
        size = self.actualSize(QSize(256, 256))
        pixmap = self.pixmap(size)
        painter = QPainter(pixmap)
        pen = QPen(color)
        pen.setWidth(0)
        painter.setPen(0)
        painter.setBrush(color)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawEllipse(x, y, w, h)
        painter.end()
        icon = QIcon(pixmap)
        self.swap(icon)
