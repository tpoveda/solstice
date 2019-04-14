#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_published_info_widget.py
# by Tomas Poveda
# Widget used to show published info in Solstice Pipelinizer Tool
# ______________________________________________________________________
# ==================================================================="""

from functools import partial
from collections import OrderedDict

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *
from pipeline.externals.solstice_qt.QtGui import *

import pipeline as sp
from pipeline.utils import qtutils
from pipeline.gui import splitters
from pipeline.resources import resource


class PublishedInfoWidget(QWidget, object):

    _error_pixmap = resource.pixmap('error', category='icons').scaled(QSize(24, 24))
    _warning_pixmap = resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
    _ok_pixmap = resource.pixmap('ok', category='icons').scaled(QSize(24, 24))
    _local_pixmap = resource.pixmap('hdd', category='icons').scaled(QSize(24, 24))
    _server_pixmap = resource.pixmap('artella', category='icons').scaled(QSize(24, 24))
    _info_pixmap = resource.pixmap('info', category='icons').scaled(QSize(24, 24))

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

        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(2, 2, 2, 2)
        scroll_layout.setSpacing(2)
        scroll_layout.setAlignment(Qt.AlignTop)
        self._versions_widget = QWidget()
        self._versions_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFocusPolicy(Qt.NoFocus)
        self.scroll.setWidget(self._versions_widget)
        self.scroll.setVisible(False)
        bottom_splitter.addWidget(self.scroll)
        self._versions_widget.setLayout(scroll_layout)
        self._versions_label = QLabel('')
        scroll_layout.addWidget(self._versions_label)

        self.update_version_info()

    def update_versions_info(self, status, file_type):
        self.scroll.setVisible(True)

    def update_version_info(self):

        qtutils.clear_layout_widgets(self._main_layout)

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
                self._ui[status]['layout'].addWidget(splitters.Splitter('WORKING INFO'))
            elif status == 'published':
                self._ui[status]['layout'].addWidget(splitters.Splitter('PUBLISHED INFO'))

            self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
            if status == 'working':
                self._info_layout.addWidget(splitters.get_horizontal_separator_widget(200))

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
                self._ui[status][f]['layout'].addWidget(splitters.get_horizontal_separator_widget())
                self._ui[status][f]['layout'].addWidget(self._ui[status][f]['label'])
                self._ui[status][f]['layout'].addWidget(splitters.get_horizontal_separator_widget())
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
                self._ui[status][f]['info_layout'].addWidget(splitters.get_horizontal_separator_widget())
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
            categories_to_check = list()
            textures_version_str = ''
            for f in sp.valid_categories:
                for status_type in ['local', 'server']:
                    if f not in max_versions[status_type].keys():
                        continue
                    version_info = max_versions[status_type][f]
                    if not version_info:
                        continue
                    if f == 'textures':
                        max_version = 0
                        for txt_name, txt_version in version_info.items():
                            # We do not check for files that have been deleted
                            if txt_version.size <= 0:
                                continue
                            if txt_version.version > max_version:
                                max_version = txt_version.version
                            textures_version_str += txt_name + ' : | ' + status_type.upper() + '| ' + 'v' + str(txt_version.version) + '\n'
                        self._ui[status][f][status_type]['text'].setText('v{0}'.format(str(max_version)))
                        self._ui[status][f]['status'].setPixmap(self._warning_pixmap)
                        self._versions_label.setText(textures_version_str)
                    else:
                        self._ui[status][f][status_type]['text'].setText('v{0}'.format(str(version_info.version)))
                        self._ui[status][f]['status'].setPixmap(self._warning_pixmap)
                    categories_to_check.append(f)
                    textures_version_str += '-----------------------\n'

                for cat in categories_to_check:
                    max_local = max_versions['local'][cat]
                    max_server = max_versions['server'][cat]

                    if cat == 'textures':
                        msg_str = ''
                        valid_check = True
                        if max_local and max_server:

                            # Clean not valid server versions
                            clean_max_server = OrderedDict()
                            for txt_name, txt_version in max_server.items():
                                if txt_version.size > 0:
                                    clean_max_server[txt_name] = txt_version

                            for local_txt_name, local_txt_version in max_local.items():

                                valid_texture = clean_max_server.get(local_txt_name)
                                server_txt_name = local_txt_name
                                if valid_texture is not None:
                                    server_txt_version = clean_max_server[local_txt_name]
                                    if local_txt_version.version == server_txt_version.version:
                                        msg_str += 'Texture {0} is updated: v{1}\n'.format(server_txt_name, server_txt_version.version)
                                    else:
                                        valid_check = False
                                        msg_str += 'Texture {0} is not updated: |LOCAL| v{1} |SERVER| v{2}'.format(server_txt_name, local_txt_version.version, server_txt_version.version)
                                else:
                                    valid_check = False
                                    msg_str += 'Invalid Texture: {0} - {1}'.format(local_txt_name, server_txt_name)
                            if valid_check:
                                self._ui[status][cat]['status'].setPixmap(self._ok_pixmap)
                                self._ui[status][cat]['status'].setToolTip('All textures are updated!')
                            else:
                                self._ui[status][cat]['status'].setPixmap(self._error_pixmap)
                                self._ui[status][cat]['status'].setToolTip(msg_str)
                        else:
                            if max_local is not None and max_server is not None and max_local.version == max_server.version:
                                self._ui[status][cat]['status'].setPixmap(self._ok_pixmap)
                                self._ui[status][cat]['status'].setToolTip('{} file is updated to last version: {}'.format(cat.title(), max_server.version))
                            elif max_local is not None and max_server is not None:
                                if max_local.version > max_server.version:
                                    self._ui[status][cat]['status'].setPixmap(self._error_pixmap)
                    else:
                        if max_local and max_server:
                            if max_local.version == max_server.version:
                                self._ui[status][cat]['status'].setPixmap(self._ok_pixmap)
                            if max_local.version > max_server.version:
                                self._ui[status][cat]['status'].setPixmap(self._error_pixmap)
                        else:
                            self._ui[status][cat]['status'].setPixmap(self._error_pixmap)

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