#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_published_info_widget.py
# by Tomas Poveda
# Widget used to show published info in Solstice Pipelinizer Tool
# ______________________________________________________________________
# ==================================================================="""

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice_pipeline as sp
from resources import solstice_resource
from solstice_utils import solstice_qt_utils
from solstice_gui import solstice_splitters

reload(solstice_qt_utils)
reload(solstice_splitters)


class PublishedInfoWidget(QWidget, object):

    _error_pixmap = solstice_resource.pixmap('error', category='icons').scaled(QSize(24, 24))
    _warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
    _ok_pixmap = solstice_resource.pixmap('ok', category='icons').scaled(QSize(24, 24))
    _local_pixmap = solstice_resource.pixmap('hdd', category='icons').scaled(QSize(24, 24))
    _server_pixmap = solstice_resource.pixmap('artella', category='icons').scaled(QSize(24, 24))
    _info_pixmap = solstice_resource.pixmap('info', category='icons').scaled(QSize(24, 24))

    def __init__(self, asset, check_published_info=False ,check_working_info=False, parent=None):
        super(PublishedInfoWidget, self).__init__(parent=parent)

        self._asset = asset
        self._check_published_info = check_published_info
        self._check_working_info = check_working_info
        self._has_model = asset.has_model()
        self._has_shading = asset.has_shading()
        self._has_textures = asset.has_textures()
        self._has_groom = asset.has_groom()

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        self._main_layout.setSpacing(5)
        self.setLayout(self._main_layout)

        self._info_layout = QHBoxLayout()
        self._info_layout.setContentsMargins(0, 0, 0, 0)
        self._info_layout.setSpacing(0)
        self._info_layout.setAlignment(Qt.AlignCenter)
        self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self._main_layout.addLayout(self._info_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(2, 2, 2, 2)
        bottom_layout.setSpacing(2)
        self._main_layout.addLayout(bottom_layout)
        self._asset_description = QTextEdit()
        self._asset_description.setReadOnly(True)
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_layout.addWidget(bottom_splitter)
        bottom_splitter.addWidget(self._asset_description)
        self._versions_widget = QWidget()
        self._versions_widget.setVisible(False)
        self._versions_layout = QVBoxLayout()
        self._versions_layout.setContentsMargins(2, 2, 2, 2)
        self._versions_layout.setSpacing(2)
        self._versions_widget.setLayout(self._versions_layout)
        bottom_splitter.addWidget(self._versions_widget)

        self.update_version_info()

    def update_versions_info(self, status, file_type):
        self._versions_widget.setVisible(True)

    def update_version_info(self):

        solstice_qt_utils.clear_layout_widgets(self._main_layout)

        folders_to_update = list()
        if self._has_model:
            folders_to_update.append('model')
        if self._has_shading:
            folders_to_update.append('shading')
        if self._has_textures:
            folders_to_update.append('textures')
        if self._has_groom:
            folders_to_update.append('groom')

        labels = dict()
        for status in ['working', 'published']:
            labels[status] = dict()
            labels[status]['model'] = QLabel('    MODEL')
            labels[status]['textures'] = QLabel('TEXTURES')
            labels[status]['shading'] = QLabel(' SHADING')
            labels[status]['groom'] = QLabel('    GROOM')

        self._ui = dict()
        for status in ['working', 'published']:
            self._ui[status] = dict()

            self._ui[status]['layout'] = QVBoxLayout()
            self._ui[status]['layout'].setContentsMargins(2, 2, 2, 2)
            self._ui[status]['layout'].setSpacing(2)
            self._info_layout.addLayout(self._ui[status]['layout'])

            if status == 'working':
                self._ui[status]['layout'].addWidget(solstice_splitters.Splitter('WORKING INFO'))
            elif status == 'published':
                self._ui[status]['layout'].addWidget(solstice_splitters.Splitter('PUBLSIHED INFO'))

            self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
            if status == 'working':
                self._info_layout.addWidget(solstice_splitters.get_horizontal_separator_widget(200))

            for f in folders_to_update:
                self._ui[status][f] = dict()
                self._ui[status][f]['layout'] = QHBoxLayout()
                self._ui[status][f]['layout'].setContentsMargins(2, 2, 2, 2)
                self._ui[status][f]['layout'].setSpacing(2)
                self._ui[status][f]['layout'].setAlignment(Qt.AlignLeft)
                self._ui[status]['layout'].addLayout(self._ui[status][f]['layout'])

                self._ui[status][f]['status'] = QLabel()
                self._ui[status][f]['status'].setPixmap(self._error_pixmap)
                self._ui[status][f]['label'] = labels[status][f]

                self._ui[status][f]['info_layout'] = QHBoxLayout()
                self._ui[status][f]['info_layout'].setContentsMargins(2, 2, 2, 2)
                self._ui[status][f]['info_layout'].setSpacing(2)

                self._ui[status][f]['layout'].addWidget(self._ui[status][f]['status'])
                self._ui[status][f]['layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                self._ui[status][f]['layout'].addWidget(self._ui[status][f]['label'])
                self._ui[status][f]['layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                self._ui[status][f]['layout'].addLayout(self._ui[status][f]['info_layout'])

                for status_type in ['local', 'server']:
                    self._ui[status][f][status_type] = dict()
                    self._ui[status][f][status_type]['layout'] = QHBoxLayout()
                    self._ui[status][f][status_type]['layout'].setContentsMargins(1, 1, 1, 1)
                    self._ui[status][f][status_type]['layout'].setSpacing(1)
                    self._ui[status][f][status_type]['layout'] = QHBoxLayout()
                    self._ui[status][f][status_type]['layout'].setContentsMargins(1, 1, 1, 1)
                    self._ui[status][f][status_type]['layout'].setSpacing(1)

                self._ui[status][f]['info_layout'].addLayout(self._ui[status][f]['local']['layout'])
                self._ui[status][f]['info_layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                self._ui[status][f]['info_layout'].addLayout(self._ui[status][f]['server']['layout'])

                for status_type in ['local', 'server']:
                    self._ui[status][f][status_type]['logo'] = QLabel()
                    if status_type == 'local':
                        self._ui[status][f][status_type]['logo'].setPixmap(self._local_pixmap)
                    else:
                        self._ui[status][f][status_type]['logo'].setPixmap(self._server_pixmap)
                    self._ui[status][f][status_type]['text'] = QLabel('None')
                    self._ui[status][f][status_type]['layout'].addWidget(self._ui[status][f][status_type]['logo'])
                    self._ui[status][f][status_type]['layout'].addWidget(self._ui[status][f][status_type]['text'])

                self._ui[status][f]['info_btn'] = QPushButton()
                self._ui[status][f]['info_btn'].setIcon(QIcon(self._info_pixmap))
                self._ui[status][f]['info_btn'].setMaximumWidth(20)
                self._ui[status][f]['info_btn'].setMaximumHeight(20)
                self._ui[status][f]['info_layout'].addWidget(self._ui[status][f]['info_btn'])

                self._ui[status][f]['info_btn'].clicked.connect(partial(self.update_versions_info, status, f))

            self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        sync_btn = QPushButton('Synchronize {0}'.format(self._asset.name))
        sync_btn.clicked.connect(self._asset.sync)
        sync_btn.setVisible(False)
        self._main_layout.addWidget(sync_btn)

        self.update_working_info()
        self.update_published_info()

    def update_working_info(self):
        if self._check_working_info:
            status = 'working'
            max_versions = self._asset.get_max_versions(status=status)
            for f in sp.valid_categories:
                for status_type in ['local', 'server']:
                    if f not in max_versions[status_type].keys():
                        continue
                    version_info = max_versions[status_type][f]
                    if f == 'textures':
                        print(version_info)
                    else:
                        if not version_info:
                            continue
                        self._ui[status][f][status_type]['text'].setText('v{0}'.format(str(version_info.version)))


    def update_published_info(self):
        if self._check_published_info:
            status = 'published'
            max_versions = self._asset.get_max_versions(status=status)
            categories_to_check = list()
            for f in sp.valid_categories:
                for status_type in ['local', 'server']:
                    if f not in max_versions[status_type].keys():
                        continue
                    version_info = max_versions[status_type][f]
                    if not version_info:
                        continue
                    self._ui[status][f][status_type]['text'].setText('v{0}'.format(str(version_info)))
                    self._ui[status][f]['status'].setPixmap(self._warning_pixmap)
                    categories_to_check.append(f)

            for cat in categories_to_check:
                max_local = max_versions['local'][cat]
                max_server = max_versions['server'][cat]

                if max_local == max_server and max_local is not None and max_server is not None:
                    self._ui[status][cat]['status'].setPixmap(self._ok_pixmap)
                if max_local > max_server or max_local is None and max_server is not None:
                    self._ui[status][cat]['status'].setPixmap(self._error_pixmap)