#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pixmap.py
# by Tomas Poveda
# Module that contains base class for Solstice Pixmaps
# ______________________________________________________________________
# ==================================================================="""

from pipeline.externals.solstice_qt.QtGui import *

from solstice_gui import solstice_color


class Pixmap(QPixmap, object):
    def __init__(self, *args):
        super(Pixmap, self).__init__(*args)

        self._color = None

    def set_color(self, new_color):
        """
        Sets pixmap's color
        :param new_color: variant (str || QColor), color to apply to the pixmap
        """

        if isinstance(new_color, str):
            new_color = solstice_color.Color.from_string(new_color)

        if not self.isNull():
            painter = QPainter(self)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.setBrush(new_color)
            painter.setPen(new_color)
            painter.drawRect(self.rect())
            painter.end()

        self._color = new_color
