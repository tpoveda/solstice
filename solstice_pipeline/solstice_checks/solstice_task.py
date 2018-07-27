#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_task.py
# by Tomas Poveda
# Module that contains base class for creating sanity check tasks
# ______________________________________________________________________
# ==================================================================="""


from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from solstice_pipeline.solstice_gui import solstice_splitters
from solstice_pipeline.resources import solstice_resource


class SanityTask(QWidget, object):
    def __init__(self, name, auto_fix=False, parent=None):
        super(SanityTask, self).__init__(parent=parent)

        self._name = name
        self._auto_fix = auto_fix
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

        self.task_name_lbl = QLabel('[{}]'.format(self._name))
        self.enable_check = QCheckBox()
        self.enable_check.setChecked(True)
        self.image_lbl = QLabel()
        self.image_separator = solstice_splitters.get_horizontal_separator_widget()
        self.image_separator.setVisible(False)
        self.task_text = QLabel()
        self.task_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.fix_btn = QPushButton('FIX')
        self.fix_btn.setVisible(False)
        self.fix_btn.setFixedWidth(40)
        self.fix_btn.clicked.connect(self.fix)
        self.fix_separator = solstice_splitters.get_horizontal_separator_widget()
        self.fix_separator.setVisible(False)

        for widget in [self.task_name_lbl, self.enable_check, solstice_splitters.get_horizontal_separator_widget(), self.image_lbl, self.image_separator, self.task_text, self.fix_separator, self.fix_btn]:
            widget_layout.addWidget(widget)

        if self._auto_fix:
            self.fix_btn.setVisible(False)
            self.fix_btn.setVisible(False)
            self.enable_check.setVisible(False)
            self.enable_check.setChecked(True)
            self.image_separator.setVisible(False)

            self.fix()

    def get_name(self):
        return self._name

    def set_error_message(self, message):
        self._error_message = message

    def get_error_message(self):
        return self._error_message

    def check(self):
        return False

    def fix(self):
        valid_check = self.check()
        if valid_check:
            self.valid_check()
            return True
        else:
            self.invalid_check()
            self.show_fix_button()
            return False

    def should_be_checked(self):
        do_check = self.enable_check.isChecked()
        if do_check:
            self.image_lbl.setText('')
            self.image_lbl.setPixmap(self._wait_pixmap)
            return True

        return False

    def show_fix_button(self):
        self.fix_btn.setVisible(not self._auto_fix)

    def set_task_text(self, text):
        self.task_text.setText(text)

    def invalid_check(self):
        self.setStyleSheet('background-color: rgb(165, 90, 90);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._error_pixmap)
        self.image_separator.setVisible(True)
        self.fix_btn.setStyleSheet('background-color: rgb(90, 90, 90);')
        self.fix_separator.setVisible(not self._auto_fix)

    def valid_check(self):
        self.setStyleSheet('background-color: rgb(45, 90, 45);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._ok_pixmap)
        self.image_separator.setVisible(True)
        self.fix_btn.setVisible(False)
        self.fix_separator.setVisible(not self._auto_fix)

