#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_task.py
# by Tomas Poveda
# Module that contains base class for creating tasks
# ______________________________________________________________________
# ==================================================================="""


from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

from solstice_pipeline.solstice_gui import solstice_splitters
from solstice_pipeline.resources import solstice_resource


class Task(QWidget, object):
    def __init__(self, name, log=None, auto_run=False, parent=None):
        super(Task, self).__init__(parent=parent)

        self._name = name
        self._log = log
        self._auto_run = auto_run
        self._valid_task = False
        self._error_message = 'Task {0} finished with errors'.format(name)

        self._error_pixmap = solstice_resource.pixmap('error', category='icons').scaled(QSize(24, 24))
        self._warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
        self._ok_pixmap = solstice_resource.pixmap('ok', category='icons').scaled(QSize(24, 24))
        self._wait_pixmap = solstice_resource.pixmap('sand_watch', category='icons').scaled(QSize(24, 24))

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.setMaximumHeight(50)
        self.setMinimumHeight(50)
        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(2, 2, 2, 2)
        widget_layout.setSpacing(0)
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        main_frame.setLineWidth(1)
        main_frame.setLayout(widget_layout)
        self.main_layout.addWidget(main_frame)

        self.check_name_lbl = QLabel('[{}]'.format(self._name))
        self.image_lbl = QLabel()
        self.image_separator = solstice_splitters.get_horizontal_separator_widget()
        self.image_separator.setVisible(False)
        self.task_text = QLabel()
        self.task_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for widget in [self.check_name_lbl, solstice_splitters.get_horizontal_separator_widget(), self.image_lbl, self.image_separator, self.task_text]:
            widget_layout.addWidget(widget)

        if self._auto_run:
            self._valid_task = self.run()

    def get_name(self):
        return self._name

    def set_error_message(self, message):
        self._error_message = message

    def set_log(self, log):
        self._log = log

    def write(self, msg):
        if self._log is None:
            return
        self._log.write(msg)
        self.repaint()

    def write_error(self, msg):
        if self._log is None:
            return
        self._log.write_error(msg)
        self.repaint()

    def write_ok(self, msg):
        if self._log is None:
            return
        self._log.write_ok(msg)
        self.repaint()

    def write_warning(self, msg):
        if self._log is None:
            return
        self._log.write_warning(msg)
        self.repaint()

    def get_error_message(self):
        return self._error_message

    def run(self):
        return False

    def set_task_text(self, text):
        self.task_text.setText(text)

    def fixing_task(self):
        self.setStyleSheet('background-color: rgb(230, 220, 30);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._warning_pixmap)
        self.image_separator.setVisible(True)

    def invalid_task(self):
        self.setStyleSheet('background-color: rgb(165, 90, 90);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._error_pixmap)
        self.image_separator.setVisible(True)

    def valid_task(self):
        self.setStyleSheet('background-color: rgb(45, 90, 45);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._ok_pixmap)
        self.image_separator.setVisible(True)
