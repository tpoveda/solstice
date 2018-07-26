#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sanitycheck.py
# by Tomas Poveda @ Original version by Irakli Kublashvili
# Solstice Pipeline tool to smooth the workflow between Maya and Artella
# ______________________________________________________________________
# ==================================================================="""

import os

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_utils import solstice_maya_utils
from solstice_gui import solstice_windows, solstice_splitters
from solstice_pipeline.resources import solstice_resource


class SanityTask(QWidget, object):
    def __init__(self, parent=None):
        super(SanityTask, self).__init__(parent=parent)

        self._error_pixmap = solstice_resource.pixmap('error', category='icons').scaled(QSize(24, 24))
        self._warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
        self._ok_pixmap = solstice_resource.pixmap('ok', category='icons').scaled(QSize(24, 24))

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

        for widget in [self.enable_check, solstice_splitters.get_horizontal_separator_widget(), self.image_lbl, self.image_separator, self.task_text, self.fix_separator, self.fix_btn]:
            widget_layout.addWidget(widget)

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
        return self.enable_check.isChecked()

    def show_fix_button(self):
        self.fix_btn.setVisible(True)

    def set_task_text(self, text):
        self.task_text.setText(text)

    def invalid_check(self):
        self.setStyleSheet('background-color: rgb(165, 90, 90);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._error_pixmap)
        self.image_separator.setVisible(True)
        self.fix_separator.setVisible(True)
        self.fix_btn.setStyleSheet('background-color: rgb(90, 90, 90);')

    def valid_check(self):
        self.setStyleSheet('background-color: rgb(45, 90, 45);')
        self.image_lbl.setText('')
        self.image_lbl.setPixmap(self._ok_pixmap)
        self.image_separator.setVisible(True)
        self.fix_separator.setVisible(False)
        self.fix_btn.setVisible(False)


class StudentLicenseCheck(SanityTask, object):
    def __init__(self, parent=None):
        super(StudentLicenseCheck, self).__init__(parent=parent)

        self.set_task_text('Check Maya Student License')

    def check(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return True

        return not solstice_maya_utils.file_has_student_line(filename=scene_path)

    def fix(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return

        solstice_maya_utils.clean_student_line(filename=scene_path)

        valid = super(StudentLicenseCheck, self).fix()
        if not valid:
            sp.logger.warning('Impossible to fix Maya Student License Check')


class SanityCheckGroup(QWidget, object):
    def __init__(self, name, parent=None):
        super(SanityCheckGroup, self).__init__(parent=parent)

        self.name = name
        self.checks = list()

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

        self.check_btn = QPushButton('Check')
        self.main_layout.addWidget(self.check_btn)
        self.check_btn.clicked.connect(self._on_do_check)

    def add_check(self, check):
        self.scroll_layout.addWidget(check)
        self.checks.append(check)

    def _on_do_check(self):
        for check in self.checks:
            if check.should_be_checked():
                valid_check = check.check()
                if valid_check:
                    check.valid_check()
                else:
                    check.invalid_check()
                    check.show_fix_button()

# ===========================================================================================================

# TODO: Read SanityGroups from JSON file and create them dynamically


class GeneralSanityCheck(SanityCheckGroup, object):
    def __init__(self, parent=None):
        super(GeneralSanityCheck, self).__init__(name='General', parent=parent)

        self.add_check(StudentLicenseCheck())


class ShadingSanityCheck(SanityCheckGroup, object):
    def __init__(self, parent=None):
        super(ShadingSanityCheck, self).__init__(name='Shading', parent=parent)

# ===========================================================================================================


class SanityCheck(solstice_windows.Window, object):

    name = 'Solstice_SanityCheck'
    title = 'Solstice Tools - Sanity Check'
    version = '1.0'
    dock = False

    def __init__(self, name='SanityCheckWindow', parent=None, **kwargs):
        super(SanityCheck, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SanityCheck, self).custom_ui()

        self.set_logo('solstice_sanitycheck_logo')

        self.checks_tab = QTabWidget()
        self.main_layout.addWidget(self.checks_tab)

        # =============================================================================

        self.add_sanity_group(GeneralSanityCheck())
        self.add_sanity_group(ShadingSanityCheck())

    def add_sanity_group(self, sanity_group):
        self.checks_tab.addTab(sanity_group, sanity_group.name)


def run():
    reload(solstice_maya_utils)
    SanityCheck.run()
