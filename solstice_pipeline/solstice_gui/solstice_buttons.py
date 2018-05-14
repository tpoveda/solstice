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


class LockButton(QPushButton, object):

    _lock_icon = solstice_resource.icon('lock')
    _unlock_icon = solstice_resource.icon('unlock')

    def __init__(self, parent=None):
        super(LockButton, self).__init__(parent=parent)
        self.setCheckable(True)
        self.unlock()
        self.toggled.connect(self.update_lock)

    def update_lock(self, isLock):
        if isLock:
            self.lock()
        else:
            self.unlock()

    def lock(self):
        self.setIcon(self._lock_icon)

    def unlock(self):
        self.setIcon(self._unlock_icon)

class CategoryButtonWidget(QWidget, object):
    def __init__(self, category_name, parent=None):
        super(CategoryButtonWidget, self).__init__(parent=parent)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(0 ,0 , 0, 0)
        widget_layout.setSpacing(0)
        main_widget = QWidget()
        main_widget.setLayout(widget_layout)
        self._category_btn = QPushButton(category_name)
        self._category_btn.setMinimumHeight(40)
        widget_layout.addWidget(self._category_btn)
        main_layout.addWidget(main_widget)

        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_frame = QFrame()
        button_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        button_frame.setLineWidth(1)
        button_frame.setLayout(button_layout)
        self._lock_btn = LockButton()
        button_layout.addWidget(self._lock_btn)
        button_frame.setParent(self)
        main_layout.addWidget(button_frame)

