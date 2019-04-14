#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Picker Window
# ==================================================================="""

import os
import weakref
from functools import partial

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *

import maya.cmds as cmds

import pipeline as sp
from pipeline.pickers.picker import utils as utils
from pipeline.gui import windowds
from pipeline.pickers.picker import pickerwidget


global window_picker


class PickerWindow(QWidget, object):

    instances = list()

    def __init__(self, picker_name, picker_title, char_name, data_path, images_path, parent=None, full_window=False):

        super(PickerWindow, self).__init__(parent=parent)

        PickerWindow._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        cmds.select(clear=True)

        self.picker_title = picker_title
        self.window_name = picker_name
        self.ui = parent
        self.char_name = char_name
        self._data_path = data_path
        self._images_path = images_path
        self._full_window = full_window

        self.body_picker_data = os.path.join(self._data_path, '{}_body_data.json'.format(self.char_name.lower()))
        self.facial_picker_data = os.path.join(self._data_path, '{}_facial_data.json'.format(self.char_name.lower()))
        self.body_picker = None
        self.facial_picker = None

        self.pickers_layout = None
        self.dock_window = None

        if not self._init_setup():
            self.close()
            return

        self.custom_ui()

        global window_picker
        window_picker = self

        self.update_pickers()

    def get_full_window(self):
        return self._full_window

    def set_full_window(self, full_window):
        self._full_window = full_window

    full_window = property(get_full_window, set_full_window)

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

        # ===============================================================================

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.load_pickers(full_window=self._full_window)
        self.update_pickers()

    def update_namespaces(self):
        self.namespace.clear()
        current_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for ns in current_namespaces:
            if ns not in ['UI', 'shared']:
                self.namespace.addItem(ns)
        self.namespace.setCurrentIndex(0)

    def load_pickers(self, full_window=False):

        if self.body_picker:
            self.body_picker.setParent(None)
            self.body_picker.deleteLater()
        if self.facial_picker:
            self.facial_picker.setParent(None)
            self.facial_picker.deleteLater()
        if self.pickers_layout:
            self.pickers_layout.setParent(None)
            self.pickers_layout.deleteLater()
        if self.dock_window:
            docks = self.dock_window._get_dock_widgets()
            for d in docks:
                d.deleteLater()
                d.close()
            self.dock_window.setParent(None)
            self.dock_window.deleteLater()
            self.dock_window.close()
            self.dock_window = None

        self.pickers_layout = QHBoxLayout()
        self.pickers_layout.setContentsMargins(5, 5, 5, 5)
        self.pickers_layout.setSpacing(2)
        self.main_layout.addLayout(self.pickers_layout)

        self.dock_window = windowds.DockWindow()
        self.main_layout.addWidget(self.dock_window)

        self.body_picker = self.get_body_picker()
        self.facial_picker = self.get_facial_picker()

        if full_window:

            main_pickers_widget = QWidget()
            main_pickers_layout = QHBoxLayout()
            main_pickers_widget.setLayout(main_pickers_layout)
            self.pickers_layout.addLayout(main_pickers_layout)
            for picker in [self.body_picker, self.facial_picker]:
                main_pickers_layout.addWidget(picker)
            self.add_tab(main_pickers_widget, 'Body & Facial')

        else:
            self.add_tab(self.body_picker, 'Body')
            self.add_tab(self.facial_picker, 'Facial')

    def run(self):
        return self

    def _init_setup(self):
        if not os.path.exists(utils.scripts_path):
            cmds.error('Solstice Picker Scripts not found!')

        sp.logger.debug('Loading pickers MEL scripts ...')

        utils.load_script('vlRigIt_getModuleFromControl.mel')
        utils.load_script('vlRigIt_getControlsFromModuleList.mel')
        utils.load_script('vlRigIt_selectModuleControls.mel')
        utils.load_script('vlRigIt_snap_ikFk.mel')
        utils.load_script('vl_resetTransformations.mel')
        utils.load_script('vl_resetAttributes.mel')
        utils.load_script('vl_contextualMenuBuilder.mel')

        return True

    def get_body_picker_data(self):
        return self.body_picker_data

    def get_facial_picker_data(self):
        return self.facial_picker_data

    def get_body_picker(self):
        return pickerwidget.Picker(
            data_path=self.get_body_picker_data(),
            image_path=os.path.join(self._images_path, '{}_body.svg'.format(self.char_name.lower())))

    def get_facial_picker(self):
        return pickerwidget.Picker(
            data_path=self.get_facial_picker_data(),
            image_path=os.path.join(self._images_path, '{}_facial.svg'.format(self.char_name.lower())))

    def update_pickers(self):
        """
        Update the state of the character pickers
        """

        for picker in [self.body_picker, self.facial_picker]:
            picker.namespace = self.namespace.currentText()

            # Called to update the FK/IK state of Picker
            picker.view.scene().update_state()

    def reload_data(self):
        """
        Relaod data used by pickers and recreate all the picker buttons and properties
        TODO: Very slow function, avoid to use it
        """

        for picker in [self.body_picker, self.facial_picker]:
            picker.reload_data()
        self.body_picker.reload_data()

    def add_dock(self, widget, name):
        dock = self.dock_window.add_dock(widget=widget, name=name)
        return dock

    def add_tab(self, widget, name):
        dock = self.add_dock(widget=widget, name=name)
        dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
