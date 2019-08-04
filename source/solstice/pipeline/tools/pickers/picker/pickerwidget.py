#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Picker Widget Class
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtWidgets import *

import maya.cmds as cmds

from solstice.pipeline.tools.pickers.picker import pickerview
from solstice.pipeline.tools.pickers.picker import commands as commands


class Picker(QWidget, object):
    def __init__(self, data_path=None, image_path=None, parent=None):
        super(Picker, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0 , 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._view = pickerview.PickerView(data_path=data_path, image_path=image_path)
        self.main_layout.addWidget(self._view)

    def get_namespace(self):
        return self._view.scene().namespace

    def set_namespace(self, namespace):
        self._view.scene().namespace = namespace

    def get_view(self):
        return self._view

    def set_view(self, view):
        if not view:
            return
        if self._view:
            self._view.setParent(None)
            self._view.deleteLater()
        self._view = view
        self.main_layout.addWidget(self._view)

    namespace = property(get_namespace, set_namespace)
    view = property(get_view, set_view)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        export_picker_data_action = menu.addAction('Export Picker Data')
        menu.addSeparator()
        select_global_action = menu.addAction('Select Global Control')
        select_all_controls_action = menu.addAction('Select All Controls')
        select_body_controls_action = menu.addAction('Select Body Controls')
        select_face_controls_action = menu.addAction('Select Face Controls')

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == export_picker_data_action:
            self.export_picker_data()
        elif action == select_global_action:
            commands.select_global_control()
        elif action == select_all_controls_action:
            commands.select_all_controls()
        elif action == select_body_controls_action:
            commands.select_body_controls()
        elif action == select_face_controls_action:
            commands.select_face_controls()

    def mousePressEvent(self, event):
        super(Picker, self).mousePressEvent(event)
        cmds.select(clear=True)

    def add_button(self):
        self.view.scene().add_button()

    def reload_data(self):
        self.view.scene().reload_data()

    def update_state(self):
        self.view.scene().udpate_scene()

    def export_picker_data(self):
        self.view.scene().get_json_file()
