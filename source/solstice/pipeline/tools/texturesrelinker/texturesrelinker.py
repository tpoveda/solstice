#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used by textures artists to relink textures path
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import maya.cmds as cmds

import solstice.pipeline as sp
from solstice.pipeline.gui import window, splitters
from solstice.pipeline.utils import mayautils, fileutils


class TexturesRelinker(window.Window, object):
    name = 'Solstice_TexturesRelinker'
    title = 'Solstice Tools - Textures Relinker'
    version = '1.0'

    def __init__(self):

        self.artella_var = os.environ.get('ART_LOCAL_ROOT')
        self.solstice_project = os.environ.get('SOLSTICE_PROJECT')

        super(TexturesRelinker, self).__init__()

        if self.artella_var is None or self.solstice_project is None:
            msgBox = QMessageBox()
            msgBox.setText(
                'Solstice environment variables are not setup correctly! Make sure you have Solstice Tools intalled and restart Maya!')
            msgBox.exec_()
            return

        self.show()

    def custom_ui(self):
        super(TexturesRelinker, self).custom_ui()

        self.set_logo('solstice_alembicmanager_logo')

        self.resize(900, 700)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        relinker_widget = RelinkerWidget(self.solstice_project)
        checker_widget = CheckerWidget()
        self.tabs.addTab(relinker_widget, 'Relinker')
        self.tabs.addTab(checker_widget, 'Checker')


class RelinkerWidget(QWidget, object):
    def __init__(self, project, parent=None):

        self.solstice_project = project

        super(RelinkerWidget, self).__init__(parent)

        relinker_layout = QVBoxLayout()
        relinker_layout.setContentsMargins(0, 0, 0, 0)
        relinker_layout.setSpacing(0)
        relinker_layout.setAlignment(Qt.AlignTop)
        self.setLayout(relinker_layout)

        paths_layout = QVBoxLayout()
        paths_layout.setContentsMargins(5, 5, 5, 5)
        paths_layout.setSpacing(2)
        relinker_layout.addLayout(paths_layout)

        target_layout = QHBoxLayout()
        target_layout.setContentsMargins(5, 5, 5, 5)
        target_layout.setSpacing(2)
        paths_layout.addLayout(target_layout)
        new_txt_lbl = QLabel('     Artella Asset Textures Folder Path: ')
        self.new_txt_line = QLineEdit()
        new_txt_btn = QPushButton('...')
        new_txt_btn.setMaximumWidth(30)
        for widget in [new_txt_lbl, self.new_txt_line, new_txt_btn]:
            target_layout.addWidget(widget)

        check_textures_btn = QPushButton('Check Textures Path')
        check_textures_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        relinker_layout.addWidget(check_textures_btn)
        relinker_layout.addLayout(splitters.SplitterLayout())

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(2, 2, 2, 2)
        options_layout.setSpacing(2)
        original_asset_name = QLabel('Original Asset Name: ')
        self.original_asset_line = QLineEdit()
        target_assset_name = QLabel('Target Asset Name: ')
        self.target_asset_name = QLineEdit()
        options_layout.addWidget(original_asset_name)
        options_layout.addWidget(self.original_asset_line)
        options_layout.addWidget(splitters.get_horizontal_separator_widget())
        options_layout.addWidget(target_assset_name)
        options_layout.addWidget(self.target_asset_name)
        relinker_layout.addLayout(options_layout)

        relinker_layout.addLayout(splitters.SplitterLayout())

        lists_layout = QHBoxLayout()
        lists_layout.setContentsMargins(5, 5, 5, 5)
        lists_layout.setSpacing(2)
        curr_list_layout = QVBoxLayout()
        curr_list_layout.setContentsMargins(5, 5, 5, 5)
        curr_list_layout.setSpacing(2)
        new_list_layout = QVBoxLayout()
        new_list_layout.setContentsMargins(5, 5, 5, 5)
        new_list_layout.setSpacing(2)
        lists_layout.addLayout(curr_list_layout)
        lists_layout.addLayout(new_list_layout)
        relinker_layout.addLayout(lists_layout)

        curr_lists_layout = QHBoxLayout()
        curr_lists_layout.setContentsMargins(5, 5, 5, 5)
        curr_lists_layout.setSpacing(2)
        bottom_curr_list_layout = QHBoxLayout()
        bottom_curr_list_layout.setContentsMargins(5, 5, 5, 5)
        bottom_curr_list_layout.setSpacing(2)
        curr_list_layout.addLayout(curr_lists_layout)
        curr_list_layout.addLayout(bottom_curr_list_layout)
        self.total_curr_txt_lbl = QLabel()
        self.total_curr_txt_lbl.setAlignment(Qt.AlignCenter)
        curr_asset_textures_path_list_layout = QVBoxLayout()
        curr_asset_textures_path_list_layout.setContentsMargins(5, 5, 5, 5)
        curr_asset_textures_path_list_layout.setSpacing(2)
        curr_lists_layout.addLayout(curr_asset_textures_path_list_layout)
        curr_asset_textures_path_list_lbl = QLabel('File Name')
        curr_asset_textures_path_list_lbl.setAlignment(Qt.AlignCenter)
        self.curr_asset_textures_path_list_names = QListWidget()
        self.curr_asset_textures_path_list_names.setMaximumWidth(200)

        curr_asset_textures_path_layout = QVBoxLayout()
        curr_asset_textures_path_layout.setContentsMargins(5, 5, 5, 5)
        curr_asset_textures_path_layout.setSpacing(2)
        curr_lists_layout.addLayout(curr_asset_textures_path_layout)

        curr_asset_textures_path_lbl = QLabel('Texture Path')
        curr_asset_textures_path_lbl.setAlignment(Qt.AlignCenter)
        self.curr_asset_textures_path_list = QListWidget()

        self.curr_textures_path_update_btn = QPushButton('Update')

        curr_asset_textures_path_list_layout.addWidget(curr_asset_textures_path_list_lbl)
        curr_asset_textures_path_list_layout.addWidget(self.curr_asset_textures_path_list_names)

        curr_asset_textures_path_layout.addWidget(curr_asset_textures_path_lbl)
        curr_asset_textures_path_layout.addWidget(self.curr_asset_textures_path_list)
        bottom_curr_list_layout.addWidget(self.curr_textures_path_update_btn)
        bottom_curr_list_layout.addWidget(self.total_curr_txt_lbl)

        new_lists_layout = QHBoxLayout()
        new_lists_layout.setContentsMargins(5, 5, 5, 5)
        new_lists_layout.setSpacing(2)
        bottom_new_list_layout = QHBoxLayout()
        bottom_new_list_layout.setContentsMargins(5, 5, 5, 5)
        bottom_new_list_layout.setSpacing(2)
        new_list_layout.addLayout(new_lists_layout)
        new_list_layout.addLayout(bottom_new_list_layout)
        self.total_new_txt_lbl = QLabel()
        self.total_new_txt_lbl.setAlignment(Qt.AlignCenter)

        new_textures_path_list_layout = QVBoxLayout()
        new_textures_path_list_layout.setContentsMargins(5, 5, 5, 5)
        new_textures_path_list_layout.setSpacing(2)
        new_lists_layout.addLayout(new_textures_path_list_layout)
        new_textures_path_list_lbl = QLabel('Valid Relinking Paths')
        new_textures_path_list_lbl.setAlignment(Qt.AlignCenter)
        self.new_textures_path_list = QListWidget()

        new_textures_no_valid_path_list_layout = QVBoxLayout()
        new_textures_no_valid_path_list_layout.setContentsMargins(5, 5, 5, 5)
        new_textures_no_valid_path_list_layout.setSpacing(2)
        new_lists_layout.addLayout(new_textures_no_valid_path_list_layout)
        new_textures_no_valid_path_list_lbl = QLabel('No Valid Relinking Paths')
        new_textures_no_valid_path_list_lbl.setAlignment(Qt.AlignCenter)
        self.new_no_valid_textures_path_list = QListWidget()
        self.new_textures_path_update_btn = QPushButton('Update')

        new_textures_path_list_layout.addWidget(new_textures_path_list_lbl)
        new_textures_path_list_layout.addWidget(self.new_textures_path_list)

        new_textures_no_valid_path_list_layout.addWidget(new_textures_no_valid_path_list_lbl)
        new_textures_no_valid_path_list_layout.addWidget(self.new_no_valid_textures_path_list)
        bottom_new_list_layout.addWidget(self.total_new_txt_lbl)
        bottom_new_list_layout.addWidget(self.new_textures_path_update_btn)

        relink_textures_btn = QPushButton('Relink Textures')
        relinker_layout.addWidget(relink_textures_btn)

        # === SIGNALS === #

        check_textures_btn.clicked.connect(self._check_new_textures)
        new_txt_btn.clicked.connect(self._set_textures_path)
        relink_textures_btn.clicked.connect(self._relink_textures)

        # ------------------------------------------------------------

        self.relinking_list = {}

        self._check_asset_textures()

    def _set_textures_path(self):
        selDir = QFileDialog.getExistingDirectory()
        if os.path.exists(selDir):
            self.new_txt_line.setText(selDir)

    def _check_new_textures(self):

        if self.new_txt_line.text() != '' and os.path.exists(self.new_txt_line.text()):
            files = [os.path.join(self.new_txt_line.text(), f) for f in os.listdir(self.new_txt_line.text())]
            files_path = list()
            curr_scenes_txts = list()
            for index in range(self.curr_asset_textures_path_list.count()):
                file_path = self.curr_asset_textures_path_list.item(index).text()
                base_path = os.path.basename(file_path)
                curr_scenes_txts.append(os.path.splitext(base_path)[0])

            renamed_items = 0

            self.relinking_list.clear()
            self.new_textures_path_list.clear()
            self.new_no_valid_textures_path_list.clear()

            for i, f in enumerate(files):

                new_path = f.replace(self.solstice_project, '$SOLSTICE_PROJECT/')
                base_file = os.path.basename(f)
                file_name = os.path.splitext(base_file)[0]

                if new_path not in files_path:
                    files_path.append(new_path)

                item = QListWidgetItem(new_path)

                if self.original_asset_line.text() and self.target_asset_name.text():
                    mod_txts = list()
                    for f in curr_scenes_txts:
                        mod_txts.append([f.replace(self.original_asset_line.text(), self.target_asset_name.text()), f])

                    for m in mod_txts:
                        if file_name == m[0]:
                            item.setBackground(Qt.green)
                            item.setForeground(Qt.black)
                            self.relinking_list[file_name] = new_path
                            renamed_items += 1
                            self.new_textures_path_list.addItem(item)
                else:
                    if file_name in curr_scenes_txts:
                        item.setBackground(Qt.green)
                        item.setForeground(Qt.black)
                        self.relinking_list[file_name] = new_path
                        renamed_items += 1
                        self.new_textures_path_list.addItem(item)
                    else:
                        self.new_no_valid_textures_path_list.addItem(item)

            self.total_new_txt_lbl.setText('Found ' + str(renamed_items) + ' textures to relink!')

    def _check_asset_textures(self):

        files = cmds.ls(type='file')
        files_path = list()

        for f in files:
            f_path = cmds.getAttr(f + '.fileTextureName')
            dir_path = os.path.split(f_path)[0]

            if dir_path not in files_path:
                files_path.append(dir_path)

            item_name = QListWidgetItem(f)
            item = QListWidgetItem(f_path)
            if 'S_PRP_' not in f:
                item_name.setBackground(Qt.yellow)
                item_name.setForeground(Qt.black)
            self.curr_asset_textures_path_list_names.addItem(item_name)
            self.curr_asset_textures_path_list.addItem(item)

        self.total_curr_txt_lbl.setText('Found ' + str(len(files)) + ' files in the asset scene!')

    @mayautils.maya_undo
    def _relink_textures(self):
        sp.logger.debug(' ========= RELINKING TEXTURES =========')
        files = cmds.ls(type='file')
        if self.new_textures_path_list.count() > 0 and len(self.relinking_list.items()) > 0:
            for file_name, file_path in self.relinking_list.iteritems():
                for i in range(self.curr_asset_textures_path_list.count()):
                    if self.original_asset_line.text() and self.target_asset_name.text():
                        mod_txt = self.curr_asset_textures_path_list.item(i).text().replace(
                            self.original_asset_line.text(), self.target_asset_name.text())
                        if file_name in mod_txt:
                            for f in files:
                                if cmds.getAttr(f + '.fileTextureName') == self.curr_asset_textures_path_list.item(
                                        i).text():
                                    sp.logger.debug('Relinking texture {} to {}'.format(mod_txt, file_path))
                                    cmds.setAttr(f + '.fileTextureName', file_path, type='string')
                    else:
                        if file_name in self.curr_asset_textures_path_list.item(i).text():
                            for f in files:
                                if cmds.getAttr(f + '.fileTextureName') == self.curr_asset_textures_path_list.item(
                                        i).text():
                                    sp.logger.debug('Relinking texture {} to {}'.format(
                                        self.curr_asset_textures_path_list.item(i).text(), file_path))
                                    cmds.setAttr(f + '.fileTextureName', file_path, type='string')


class CheckerWidget(QWidget, object):
    def __init__(self, parent=None):
        super(CheckerWidget, self).__init__(parent)

        relinker_layout = QVBoxLayout()
        relinker_layout.setContentsMargins(0, 0, 0, 0)
        relinker_layout.setSpacing(0)
        relinker_layout.setAlignment(Qt.AlignTop)
        self.setLayout(relinker_layout)

        self.file_paths = QListWidget()
        relinker_layout.addWidget(self.file_paths)

        self._update_file_paths()

    def _update_file_paths(self):
        self.file_paths.clear()
        for f in fileutils.get_file_paths():
            self.file_paths.addItem(f)


def run():
    TexturesRelinker().show()
