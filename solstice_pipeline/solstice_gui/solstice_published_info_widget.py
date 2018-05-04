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
        self._has_model = True
        self._has_shading = True
        self._has_textures = True
        self._has_groom = False

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

        ui = dict()
        for status in ['working', 'published']:
            ui[status] = dict()

            ui[status]['layout'] = QVBoxLayout()
            ui[status]['layout'].setContentsMargins(2, 2, 2, 2)
            ui[status]['layout'].setSpacing(2)
            self._info_layout.addLayout(ui[status]['layout'])

            if status == 'working':
                ui[status]['layout'].addWidget(solstice_splitters.Splitter('WORKING INFO'))
            elif status == 'published':
                ui[status]['layout'].addWidget(solstice_splitters.Splitter('PUBLSIHED INFO'))

            self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
            if status == 'working':
                self._info_layout.addWidget(solstice_splitters.get_horizontal_separator_widget(200))

            for f in folders_to_update:
                ui[status][f] = dict()
                ui[status][f]['layout'] = QHBoxLayout()
                ui[status][f]['layout'].setContentsMargins(2, 2, 2, 2)
                ui[status][f]['layout'].setSpacing(2)
                ui[status][f]['layout'].setAlignment(Qt.AlignLeft)
                ui[status]['layout'].addLayout(ui[status][f]['layout'])

                ui[status][f]['status'] = QLabel()
                ui[status][f]['status'].setPixmap(self._error_pixmap)
                ui[status][f]['label'] = labels[status][f]

                ui[status][f]['info_layout'] = QHBoxLayout()
                ui[status][f]['info_layout'].setContentsMargins(2, 2, 2, 2)
                ui[status][f]['info_layout'].setSpacing(2)

                ui[status][f]['layout'].addWidget(ui[status][f]['status'])
                ui[status][f]['layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                ui[status][f]['layout'].addWidget(ui[status][f]['label'])
                ui[status][f]['layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                ui[status][f]['layout'].addLayout(ui[status][f]['info_layout'])

                for status_type in ['local', 'server']:
                    ui[status][f][status_type] = dict()
                    ui[status][f][status_type]['layout'] = QHBoxLayout()
                    ui[status][f][status_type]['layout'].setContentsMargins(1, 1, 1, 1)
                    ui[status][f][status_type]['layout'].setSpacing(1)
                    ui[status][f][status_type]['layout'] = QHBoxLayout()
                    ui[status][f][status_type]['layout'].setContentsMargins(1, 1, 1, 1)
                    ui[status][f][status_type]['layout'].setSpacing(1)

                ui[status][f]['info_layout'].addLayout(ui[status][f]['local']['layout'])
                ui[status][f]['info_layout'].addWidget(solstice_splitters.get_horizontal_separator_widget())
                ui[status][f]['info_layout'].addLayout(ui[status][f]['server']['layout'])

                for status_type in ['local', 'server']:
                    ui[status][f][status_type]['logo'] = QLabel()
                    if status_type == 'local':
                        ui[status][f][status_type]['logo'].setPixmap(self._local_pixmap)
                    else:
                        ui[status][f][status_type]['logo'].setPixmap(self._server_pixmap)
                    ui[status][f][status_type]['text'] = QLabel('None')
                    ui[status][f][status_type]['layout'].addWidget(ui[status][f][status_type]['logo'])
                    ui[status][f][status_type]['layout'].addWidget(ui[status][f][status_type]['text'])

                ui[status][f]['info_btn'] = QPushButton()
                ui[status][f]['info_btn'].setIcon(QIcon(self._info_pixmap))
                ui[status][f]['info_btn'].setMaximumWidth(20)
                ui[status][f]['info_btn'].setMaximumHeight(20)
                ui[status][f]['info_layout'].addWidget(ui[status][f]['info_btn'])

                ui[status][f]['info_btn'].clicked.connect(partial(self.update_versions_info, status, f))

            self._info_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        sync_btn = QPushButton('Synchronize {0}'.format(self._asset.name))
        sync_btn.clicked.connect(self._asset.sync)
        sync_btn.setVisible(False)
        self._main_layout.addWidget(sync_btn)

        # Update Working Info
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
                        # TODO: Check if necessary use sync time to know if we have a proper version of the working asset
                        ui[status][f][status_type]['text'].setText('v{0}'.format(str(version_info.version)))

        # Update Published Info
        if self._check_published_info:
            print('Checking Published Info ...')
            status = 'published'
            max_versions = self._asset.get_max_versions(status=status)
            for f in sp.valid_categories:
                for status_type in ['local', 'server']:
                    if f not in max_versions[status_type].keys():
                        continue
                    version_info = max_versions[status_type][f]
                    if not version_info:
                        continue
                    # TODO: Check if necessary use sync time to know if we have a proper version of the working asset
                    ui[status][f][status_type]['text'].setText('v{0}'.format(str(version_info)))

        # status = 'working'
        # if self._check_versions:
        #     max_versions = self._asset.get_max_versions('working')
        #     local_versions = max_versions['local']
        #     server_versions = max_versions['server']
            # for (local_f, local_version), (server_f, server_version) in zip(local_versions.items(), server_versions.items()):
            #     if local_f in folders_to_update and server_f in folders_to_update:
            #         ui[status][]


        # status = 'published'
        # if self._check_versions:
        #     max_versions = self._asset.get_max_versions()
        #     local_versions = max_versions['local']
        #     server_versions = max_versions['server']
        #     for (local_f, local_version), (server_f, server_version) in zip(local_versions.items(), server_versions.items()):
        #         if local_f in folders_to_update and server_f in folders_to_update:
        #             ui[status][local_f]['status'].setPixmap(self._error_pixmap)
        #             if local_version:
        #                 ui[status][local_f]['local_text'].setText(str('v{0}'.format(str(local_version))))
        #                 ui[status][local_f]['status'].setPixmap(self._warning_pixmap)
        #             else:
        #                 ui[status][local_f]['local_text'].setText('None')
        #
        #             if server_version:
        #                 ui[status][server_f]['server_text'].setText(str('v{0}'.format(str(server_version))))
        #                 ui[status][server_f]['status'].setPixmap(self._warning_pixmap)
        #             else:
        #                 ui[status][server_f]['server_text'].setText('None')
        #
        #             if local_version == server_version and local_version is not None and server_version is not None:
        #                 ui[status][local_f]['status'].setPixmap(self._ok_pixmap)
        #
        #             if local_version > server_version or local_version is None and server_version is not None:
        #                 ui[status][local_f]['status'].setPixmap(self._error_pixmap)
        #                 sync_btn.setVisible(True)
        # else:
        #     max_local_versions = self._asset.get_max_local_versions()
        #     for f in folders:
        #         if f in folders_to_update:
        #             if max_local_versions[f]:
        #                 ui[status][f]['local_text'].setText(str('v{0}'.format(str(max_local_versions[f][0]))))
        #                 ui[status][f]['status'].setPixmap(self._warning_pixmap)
        #             else:
        #                 ui[status][f]['local_text'].setText('None')
        #                 ui[status][f]['status'].setPixmap(self._error_pixmap)
        #
        # # Update Working Info
        # status = 'working'
        # locals = self._asset.get_local_versions(status=status)
        # if not locals:
        #     return
        #
        # for f, file_data in locals.items():
        #     if not file_data:
        #         continue
        #
        #     if not file_data.versions:
        #         continue
        #
        #     for version in file_data.versions:
        #         print(version[1].date_created)

            # print('asdfasfasf')
            # print(version_data)
            # print(version_data.date_created)



        # last_version = locals[-1]
        # print(last_version[1].name)
        # print(last_version)




