
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_animmanager.py
# by Tomas Poveda
# ______________________________________________________________________
# ==================================================================="""

import os

import maya.cmds as cmds

from pipeline.externals.solstice_qt.QtWidgets import *

import solstice_studiolibrarymaya
solstice_studiolibrarymaya.registerItems()
solstice_studiolibrarymaya.enableMayaClosedEvent()
import solstice_studiolibrary.librarywidget

import pipeline as sp
from pipeline.gui import windowds, splitters


class StudioLibrary(windowds.Window, object):
    name = 'Solstice_StudioLibrary'
    title = 'Solstice Tools - Studio Library'
    version = '2.4.0b2'

    def __init__(self):
        super(StudioLibrary, self).__init__()

    def custom_ui(self):
        super(StudioLibrary, self).custom_ui()

        self.logo_view.setVisible(False)

        self.resize(700, 700)

        namespace_layout = QHBoxLayout()
        namespace_layout.setContentsMargins(5, 5, 5, 5)
        namespace_layout.setSpacing(2)
        namespace_lbl = QLabel('Charater namespace: ')
        namespace_lbl.setMaximumWidth(115)
        reload_namespaces_btn = QPushButton('Reload')
        reload_namespaces_btn.setMaximumWidth(50)
        self.namespace = QComboBox()
        self.namespace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        namespace_layout.addWidget(namespace_lbl)
        namespace_layout.addWidget(self.namespace)
        namespace_layout.addWidget(reload_namespaces_btn)
        self.main_layout.addLayout(namespace_layout)

        namespace_layout.addWidget(splitters.get_horizontal_separator_widget())

        select_all_controls_btn = QPushButton('Select All Controls')
        namespace_layout.addWidget(select_all_controls_btn)

        self.main_layout.addLayout(splitters.SplitterLayout())

        solstice_project_folder = os.environ.get('SOLSTICE_PROJECT', None)
        if solstice_project_folder is None:
            sp.update_solstice_project_path()
            solstice_project_folder = os.environ.get('SOLSTICE_PROJECT')

        self.pose_widget = solstice_studiolibrary.LibraryWidget.instance(show=False)

        # self.pose_widget = solstice_studiolibrary.main(show=False)

        if solstice_project_folder and os.path.exists(solstice_project_folder):
            solstice_assets = os.path.join(solstice_project_folder, 'Assets', 'Scripts', 'PIPELINE', '__working__')
            if os.path.exists(solstice_assets):
                anims = os.path.join(solstice_assets, 'AnimationLibrary')
                if os.path.exists(anims):
                    self.pose_widget.setPath(anims)
                else:
                    self.pose_widget.setPath(solstice_assets)
            else:
                self.pose_widget.setPath(solstice_project_folder)

        self.pose_widget.show()

        self.main_layout.addWidget(self.pose_widget)

        reload_namespaces_btn.clicked.connect(self.update_namespaces)
        select_all_controls_btn.clicked.connect(self.select_all_controls)

        self.update_namespaces()

    def update_namespaces(self):
        self.namespace.clear()
        current_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for ns in current_namespaces:
            if ns not in ['UI', 'shared']:
                self.namespace.addItem(ns)
        self.namespace.setCurrentIndex(0)

    def select_all_controls(self, replace=True):
        ctrl = '{}:{}'.format(self.namespace.currentText(), 'CTRLs_set')
        if cmds.objExists(ctrl):
            cmds.select(ctrl, replace=replace, add=not replace)

def run():
    StudioLibrary().show()
