#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_button.py
# by Tomas Poveda
# Module that contains different buttons used in Solstice Tools
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from resources import solstice_resource


class IconButton(QPushButton, object):
    def __init__(self, icon_name='', button_text='', icon_padding=0, icon_min_size=8, icon_extension='png', parent=None):
        super(IconButton, self).__init__(parent=parent)

        self._pad = icon_padding
        self._minSize = icon_min_size

        self.setIcon(solstice_resource.icon(name=icon_name, extension=icon_extension))
        self.setStyleSheet('QPushButton { background-color: rgba(255, 255, 255, 0); border:0px; }')
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        rect = opt.rect
        icon_size = max(min(rect.height(), rect.width()) - 2 * self._pad, self._minSize)
        opt.iconSize = QSize(icon_size, icon_size)
        self.style().drawControl(QStyle.CE_PushButton, opt, painter, self)
        painter.end()