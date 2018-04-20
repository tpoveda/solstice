#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_artella_utils.py
# by Tomas Poveda
# Module that contains base class for Solstice Icons
#  with Artella
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtGui import *
from Qt.QtCore import *

from solstice_gui import solstice_color


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
            new_color = solstice_color.Color.from_string(new_color)

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


