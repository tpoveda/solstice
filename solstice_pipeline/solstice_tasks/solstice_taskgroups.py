#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_taskgroups.py
# by Tomas Poveda
# Module that contains base class for creating task groups
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *


class TaskGroup(QWidget, object):
    taskDone = Signal(object, bool)
    taskFinished = Signal(bool)

    def __init__(self, name, log=None, stop_on_error=False, parent=None):
        super(TaskGroup, self).__init__(parent=parent)

        self.name = name
        self.stop_on_error = stop_on_error
        self.tasks = list()
        self.log = log

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_widget.setLayout(self.scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll_widget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.main_layout.addWidget(scroll)

    def add_task(self, task):
        task.image_lbl.setPixmap(task._wait_pixmap)
        task.set_log(self.log)
        self.scroll_layout.addWidget(task)
        self.tasks.append(task)

    def set_log(self, log):
        self.log = log

    def _on_do_task(self):
        valid_task = True
        for task in self.tasks:
            valid_task = task.run()
            if valid_task:
                task.valid_task()
                self.taskDone.emit(task, True)
            else:
                task.invalid_task()
                self.taskDone.emit(task, False)
                if self.stop_on_error:
                    break
                valid_task = False

        self.taskFinished.emit(valid_task)
