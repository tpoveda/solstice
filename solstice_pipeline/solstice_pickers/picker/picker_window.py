#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Picker Window
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import os
import weakref
from functools import partial

import maya.cmds as cmds

from solstice_pipeline.solstice_pickers.picker import picker_utils as utils


global window_picker


class PickerWindow(QWidget, object):

    instances = list()

    def __init__(self, picker_name, picker_title, char_name, parent=None):
        super(PickerWindow, self).__init__(parent=parent)

        PickerWindow._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        self.picker_title = picker_title
        self.window_name = picker_name
        self.ui = parent
        self.char_name = char_name
        cmds.select(clear=True)
        self.custom_ui()
        global window_picker
        window_picker = self

        if not self._init_setup():
            self.close()
            return

    @staticmethod
    def _delete_instances():
        for ins in PickerWindow.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
            except Exception:
                pass

            PickerWindow.instances.remove(ins)
            del ins

    def custom_ui(self):

        # Menu bar
        menubar_widget = QWidget()
        menubar_layout = QVBoxLayout()
        menubar_widget.setLayout(menubar_layout)
        menubar = QMenuBar()
        settings_file = menubar.addMenu('Settings')
        self.fullscreen_action = QAction('FullScreen', menubar_widget, checkable=True)
        settings_file.addAction(self.fullscreen_action)
        menubar_layout.addWidget(menubar)
        self.parent().layout().addWidget(menubar_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setFocusPolicy(Qt.NoFocus)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.parent().layout().addWidget(self.scroll_area)

        self._main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 25, 5, 5)
        self.main_layout.setAlignment(Qt.AlignTop)
        self._main_widget.setLayout(self.main_layout)
        self.scroll_area.setWidget(self._main_widget)

        namespace_layout = QHBoxLayout()
        namespace_layout.setContentsMargins(5, 5, 5, 5)
        namespace_layout.setSpacing(2)
        namespace_lbl = QLabel('Charater namespace: ')
        namespace_lbl.setMaximumWidth(115)
        reload_namespaces_btn = QPushButton('Reload')
        reload_namespaces_btn.setMaximumWidth(50)
        self.namespace = QComboBox()
        namespace_layout.addWidget(namespace_lbl)
        namespace_layout.addWidget(self.namespace)
        namespace_layout.addWidget(reload_namespaces_btn)
        self.main_layout.addLayout(namespace_layout)

        reload_namespaces_btn.clicked.connect(self.update_namespaces)
        self.fullscreen_action.toggled.connect(partial(self.load_pickers))

        self.update_namespaces()

    def update_namespaces(self):
        current_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for ns in current_namespaces:
            if ns not in ['UI', 'shared']:
                self.namespace.addItem(ns)
        self.namespace.setCurrentIndex(0)

    def load_pickers(self, full_window=False):
        return

    def run(self):
        return self

    def _init_setup(self):
        if not os.path.exists(utils.scripts_path):
            cmds.error('Solstice Picker Scripts not found!')

        utils.load_script('vlRigIt_getModuleFromControl.mel')
        utils.load_script('vlRigIt_getControlsFromModuleList.mel')
        utils.load_script('vlRigIt_selectModuleControls.mel')
        utils.load_script('vlRigIt_snap_ikFk.mel')
        utils.load_script('vl_resetTransformations.mel')
        utils.load_script('vl_resetAttributes.mel')
        utils.load_script('vl_contextualMenuBuilder.mel')

        return True
