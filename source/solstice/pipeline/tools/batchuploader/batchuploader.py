#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to upload new working versions of files to Artella in a batch mode
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.gui import window, splitters
from solstice.pipeline.resources import resource


class BatchUploader(window.Window, object):

    name = 'SolsticeBatchUploader'
    title = 'Solstice Tools - Artella Batch Uploader'
    version = '1.0'

    def __init__(self):
        super(BatchUploader, self).__init__()

    def custom_ui(self):
        super(BatchUploader, self).custom_ui()

        self.resize(350, 650)

        self.main_layout.setAlignment(Qt.AlignTop)

        self._path_widget = QWidget()
        path_layout = QVBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(0)
        path_base_layout = QHBoxLayout()
        path_base_layout.setContentsMargins(0, 0, 0, 0)
        path_base_layout.setSpacing(0)
        path_layout.addLayout(path_base_layout)
        self._path_widget.setLayout(path_layout)
        path_lbl = QLabel('Path: ')
        path_lbl.setFixedWidth(30)
        self._folder_path = QLineEdit()
        tip = 'Select folder where files to batch are located'
        self._folder_path.setToolTip(tip)
        self._folder_path.setStatusTip(tip)
        self._folder_path.setContextMenuPolicy(Qt.CustomContextMenu)
        browse_icon = resource.icon('open')
        self._browse_btn = QPushButton()
        self._browse_btn.setIcon(browse_icon)
        self._browse_btn.setFixedWidth(30)
        self._browse_btn.setToolTip('Browse Root Folder')
        self._browse_btn.setStatusTip('Browse Root Folder')
        path_base_layout.addWidget(path_lbl)
        path_base_layout.addWidget(self._folder_path)
        path_base_layout.addWidget(self._browse_btn)

        self._all_cbx = QCheckBox()
        self._all_cbx.setChecked(True)
        cbx_lyt = QHBoxLayout()
        cbx_lyt.setContentsMargins(0, 0, 0, 0)
        cbx_lyt.setSpacing(0)
        cbx_lyt.addWidget(self._all_cbx)
        cbx_lyt.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        self._files_list = QListWidget()
        self._files_list.setAlternatingRowColors(True)

        self._upload_btn = QPushButton('Upload')

        self.main_layout.addWidget(self._path_widget)
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addLayout(cbx_lyt)
        self.main_layout.addWidget(self._files_list)
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addWidget(self._upload_btn)

        self._browse_btn.clicked.connect(self._on_browse)
        self._all_cbx.toggled.connect(self._on_toggle_all)

    def _refresh_files(self):
        root_path = self._folder_path.text()
        if not root_path:
            return

        self._files_list.clear()

        for root, dirs, files in os.walk(root_path):
            for f in files:
                file_path = '{}{}{}'.format(root, os.sep, f)
                list_item = QListWidgetItem(os.path.relpath(file_path, root_path), self._files_list)
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                if self._all_cbx.isChecked():
                    list_item.setCheckState(Qt.Checked)
                else:
                    list_item.setCheckState(Qt.Unchecked)
                self._files_list.addItem(list_item)

    def _on_browse(self):

        stored_path = self.settings.get('upload_path')
        if stored_path and os.path.isdir(stored_path):
            start_directory = stored_path
        else:
            start_directory = sp.get_solstice_project_path()

        export_path = sys.solstice.dcc.select_folder_dialog(
            title='Select Root Path',
            start_directory=start_directory
        )
        if not export_path:
            return

        self.settings.set(self.settings.app_name, 'upload_path', str(export_path))
        self.settings.update()

        self._folder_path.setText(export_path)

        self._refresh_files()

    def _on_toggle_all(self, flag):
        for i in range(self._files_list.count()):
            item = self._files_list.item(i)
            if flag:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

def run():
    BatchUploader().show()
