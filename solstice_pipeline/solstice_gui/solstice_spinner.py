#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_publisher.py
# by Tomas Poveda
# Tool that is used to publish assets and sequences
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from solstice_pipeline.solstice_gui import solstice_label
from resources import solstice_resource


class SpinnerType(object):
    Thumb = 'thumb'
    Circle = 'circle'

class WaitSpinner(QWidget, object):
    def __init__(self, spinner_type=SpinnerType.Thumb, parent=None):
        super(WaitSpinner, self).__init__(parent=parent)

        empty_thumb = solstice_resource.pixmap('empty_file', category='icons')

        self._spin_icons = list()

        if spinner_type == SpinnerType.Thumb:
            for i in range(7):
                self._spin_icons.append(solstice_resource.pixmap('thumb_loading_{}'.format(i+1), category='icons'))
        else:
            for i in range(10):
                self._spin_icons.append(solstice_resource.pixmap('circle_loading_{}'.format(i+1), category='icons'))

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

        self.thumbnail_label = solstice_label.ThumbnailLabel()
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
