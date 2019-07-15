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
from solstice.pipeline.utils import artellautils as artella
from solstice.pipeline.resources import resource


class BatchUploader(window.Window, object):

    name = 'SolsticeBatchUploader'
    title = 'Solstice Tools - Artella Batch Uploader'
    version = '1.0'

    def __init__(self):
        super(BatchUploader, self).__init__()

    def custom_ui(self):
        super(BatchUploader, self).custom_ui()

        self.resize(450, 650)

        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
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

        self._files_list = QTreeWidget()
        self._files_list.setColumnCount(4)
        self._files_list.setAlternatingRowColors(True)
        self._files_list.setHeaderLabels(['', 'Path', 'Current Version', 'New Version'])
        for i in range(4):
            self._files_list.resizeColumnToContents(i)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }");
        self._progress_lbl = QLabel('')
        self._progress_lbl.setAlignment(Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(2, 2, 2, 2)
        buttons_layout.setSpacing(2)
        self._lock_btn = QPushButton('Lock')
        self._upload_btn = QPushButton('Upload')
        self._unlock_btn = QPushButton('Unlock')
        buttons_layout.addWidget(self._lock_btn)
        buttons_layout.addWidget(self._upload_btn)
        buttons_layout.addWidget(self._unlock_btn)

        self.main_layout.addWidget(self._path_widget)
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addLayout(cbx_lyt)
        self.main_layout.addWidget(self._files_list)
        self.main_layout.addWidget(self._progress)
        self.main_layout.addWidget(self._progress_lbl)
        self.main_layout.addLayout(buttons_layout)

        self._browse_btn.clicked.connect(self._on_browse)
        self._all_cbx.toggled.connect(self._on_toggle_all)
        self._lock_btn.clicked.connect(self._on_lock)
        self._upload_btn.clicked.connect(self._on_upload)
        self._unlock_btn.clicked.connect(self._on_unlock)

    def _refresh_files(self):
        root_path = self._folder_path.text()
        if not root_path:
            return

        self._files_list.clear()

        for root, dirs, files in os.walk(root_path):
            for f in files:
                file_path = '{}{}{}'.format(root, os.sep, f)
                list_item = QTreeWidgetItem(self._files_list, [None, os.path.relpath(file_path, root_path), self._files_list])
                list_item.path = file_path
                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setTextAlignment(2, Qt.AlignCenter)
                list_item.setTextAlignment(3, Qt.AlignCenter)
                if self._all_cbx.isChecked():
                    list_item.setCheckState(0, Qt.Checked)
                else:
                    list_item.setCheckState(0, Qt.Unchecked)

        for i in range(4):
            self._files_list.resizeColumnToContents(i)

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
        self._refresh_versions()

    def _on_toggle_all(self, flag):
        it = QTreeWidgetItemIterator(self._files_list)
        while it.value():
            item = it.value()
            if flag:
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            it += 1

    def _checked_items(self):
        """
        Internal function that returns all checked items in the list
        :return: generator
        """

        it = QTreeWidgetItemIterator(self._files_list)
        while it.value():
            item = it.value()
            if item.checkState(0) == Qt.Checked:
                yield item
            it += 1

    def _all_items(self):
        """
        Internal function that updates the versions of all items
        :return: generator
        """

        it = QTreeWidgetItemIterator(self._files_list)
        while it.value():
            item = it.value()
            yield item
            it += 1

    def _refresh_versions(self):
        """
        Internal funciton that updates working version of selected items
        :return:
        """

        all_items = list(self._all_items())
        self._progress.setVisible(True)
        self._progress.setMinimum(0)
        self._progress.setMaximum(len(all_items)-1)
        self._progress_lbl.setText('Checking file versions ... Please wait!')
        for i, item in enumerate(all_items):
            self._progress.setValue(i)
            self._progress_lbl.setText('Checking version for: {}'.format(item.text(1)))
            current_version = artella.get_file_current_working_version(item.path)
            if current_version == 0:
                item.setText(2, '0 (Local Only)')
            else:
                item.setText(2, str(current_version))
            item.setText(3, str(current_version + 1))
        self._progress.setValue(0)
        self._progress_lbl.setText('')
        self._progress.setVisible(False)

    def _on_lock(self):
        items_to_lock = list()
        checked_items = self._checked_items()
        for item in checked_items:
            if not os.path.isfile(item.path):
                continue
            items_to_lock.append(item)

        if not items_to_lock:
            return

        self._progress.setVisible(True)
        self._progress.setMinimum(0)
        self._progress.setMaximum(len(items_to_lock)-1)
        self._progress_lbl.setText('Locking files ...')
        for i, item in enumerate(items_to_lock):
            self._progress.setValue(i)
            self._progress_lbl.setText('Locking: {}'.format(item.text(1)))
            sp.lock_file(item.path, notify=False)
        self._progress.setValue(0)
        self._progress_lbl.setText('')
        self._progress.setVisible(False)
        sys.solstice.tray.show_message(title='Lock Files', msg='Files locked successfully!')

    def _on_unlock(self):
        items_to_unlock = list()
        checked_items = self._checked_items()
        for item in checked_items:
            if not os.path.isfile(item.path):
                continue
            items_to_unlock.append(item)

        if not items_to_unlock:
            return

        msg = 'If changes in files are not submitted to Artella yet, submit them before unlocking the file please. \n\n Do you want to continue?'
        res = sys.solstice.dcc.confirm_dialog(title='Solstice Tools - Unlock File', message=msg, button=['Yes', 'No'], cancel_button='No', dismiss_string='No')
        if sp.is_houdini():
            if res != QMessageBox.StandardButton.Yes:
                return
        else:
            if res != 'Yes':
                return False

        self._progress.setVisible(True)
        self._progress.setMinimum(0)
        self._progress.setMaximum(len(items_to_unlock) - 1)
        self._progress_lbl.setText('Unlocking files ...')
        for i, item in enumerate(items_to_unlock):
            self._progress.setValue(i)
            self._progress_lbl.setText('Unlocking: {}'.format(item.text(1)))
            sp.unlock_file(item.path, notify=False, warn_user=False)
        self._progress.setValue(0)
        self._progress_lbl.setText('')
        self._progress.setVisible(False)
        sys.solstice.tray.show_message(title='Unlock Files', msg='Files unlocked successfully!')

    def _on_upload(self):
        items_to_upload = list()
        checked_items = self._checked_items()
        for item in checked_items:
            if not os.path.isfile(item.path):
                continue
            items_to_upload.append(item)

        if not items_to_upload:
            return

        try:
            comment, res = QInputDialog.getMultiLineText(sys.solstice.dcc.get_main_window(), 'Make New Versions', 'Comment')
        except Exception:
            comment, res = QInputDialog.getText(sys.solstice.dcc.get_main_window(),'Make New Versions', 'Comment')

        if res and comment:
            self._progress.setVisible(True)
            self._progress.setMinimum(0)
            self._progress.setMaximum(len(items_to_upload)-1)
            self._progress_lbl.setText('Uploading new working versions to Artella server ...')
            for i, item in enumerate(items_to_upload):
                self._progress.setValue(i)
                self._progress_lbl.setText('New version for: {} ({})'.format(item.text(1), item.text(3)))
                sp.upload_working_version(item.path, skip_saving=True, notify=False, comment=comment)
            self._progress.setValue(0)
            self._progress_lbl.setText('')
            self._progress.setVisible(False)
            sys.solstice.tray.show_message(title='New Working Versions', msg='New versions uploaded to Artella server successfully!')


def run():
    BatchUploader().show()
