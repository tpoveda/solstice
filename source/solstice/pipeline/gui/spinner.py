#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to create wait spinners
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


from Qt.QtCore import *
from Qt.QtWidgets import *

from solstice.pipeline.gui import label
from solstice.pipeline.resources import resource


class SpinnerType(object):
    Thumb = 'thumb'
    Circle = 'circle'
    Loading = 'loading'


class WaitSpinner(QWidget, object):
    def __init__(self, spinner_type=SpinnerType.Thumb, parent=None):
        super(WaitSpinner, self).__init__(parent=parent)

        empty_thumb = resource.pixmap('empty_file', category='icons')

        self._spin_icons = list()

        if spinner_type == SpinnerType.Thumb:
            for i in range(7):
                self._spin_icons.append(resource.pixmap('thumb_working_{}'.format(i + 1), category='icons'))
        elif spinner_type == SpinnerType.Loading:
            for i in range(7):
                self._spin_icons.append(resource.pixmap('thumb_loading_{}'.format(i + 1), category='icons'))
        else:
            for i in range(10):
                self._spin_icons.append(resource.pixmap('circle_loading_{}'.format(i + 1), category='icons'))

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self.bg = QFrame(self)
        self.bg.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.bg.setFrameShape(QFrame.StyledPanel)
        self.bg.setFrameShadow(QFrame.Raised)
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setContentsMargins(4, 4, 4, 4)
        self.bg.setLayout(self.frame_layout)
        main_layout.addWidget(self.bg)

        self.thumbnail_label = label.ThumbnailLabel()
        self.thumbnail_label.setMinimumSize(QSize(80, 55))
        self.thumbnail_label.setMaximumSize(QSize(80, 55))
        self.thumbnail_label.setStyleSheet('')
        self.thumbnail_label.setPixmap(empty_thumb)
        self.thumbnail_label.setScaledContents(False)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.frame_layout.addWidget(self.thumbnail_label)

        self._current_spinner_index = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_update_spinner)

    def showEvent(self, event):
        if not self._timer.isActive():
            self._timer.start(100)
        super(WaitSpinner, self).showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super(WaitSpinner, self).hideEvent(event)

    def closeEvent(self, event):
        self._timer.stop()
        super(WaitSpinner, self).closeEvent(event)

    def _on_update_spinner(self):
        self.thumbnail_label.setPixmap(self._spin_icons[self._current_spinner_index])
        self._current_spinner_index += 1
        if self._current_spinner_index == len(self._spin_icons):
            self._current_spinner_index = 0
