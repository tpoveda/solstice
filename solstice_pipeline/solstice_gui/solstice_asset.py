#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_asset.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

import os
import time
import webbrowser
import collections
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice_pipeline as sp
from solstice_utils import solstice_image as img
from solstice_utils import solstice_artella_utils as artella
from solstice_utils import solstice_artella_classes, solstice_qt_utils, solstice_python_utils
from solstice_gui import solstice_splitters, solstice_published_info_widget, solstice_sync_dialog
from resources import solstice_resource

reload(img)
reload(artella)
reload(solstice_artella_classes)
reload(solstice_qt_utils)
reload(solstice_python_utils)
reload(solstice_splitters)
reload(solstice_published_info_widget)
reload(solstice_sync_dialog)
reload(solstice_resource)

# ================================================================================================================


def generate_asset_widget_by_category(**kwargs):
    if not 'category' in kwargs:
        return None
    category = kwargs['category']

    if category == 'Characters':
        return CharacterAsset(**kwargs)
    elif category == 'Props':
        return PropAsset(**kwargs)
    elif category == 'Background Elements':
        return BackgroundElementAsset(**kwargs)

    return None


class AssetInfo(QWidget, object):
    """
    This class is instantiated by the asset widget when necessary and is used by Pipelinizer Tool
    to show information of the widget itself
    """

    def __init__(self, asset, check_versions=False):
        super(AssetInfo, self).__init__()

        self._check_versions = check_versions

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self._asset_info_lbl = solstice_splitters.Splitter(asset.name)
        self._asset_icon = QLabel()
        self._asset_icon.setPixmap(solstice_resource.pixmap('empty_file', category='icons').scaled(200, 200, Qt.KeepAspectRatio))
        self._asset_icon.setAlignment(Qt.AlignCenter)
        self._buttons_layout = QHBoxLayout()
        self._buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._buttons_layout.setSpacing(1)
        self._asset_buttons_layout = QVBoxLayout()
        self._asset_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._asset_buttons_layout.setSpacing(1)
        self._asset_buttons_layout.setAlignment(Qt.AlignTop)
        self._buttons_layout.addLayout(self._asset_buttons_layout)
        asset_tab = QTabWidget()
        asset_tab.setMaximumHeight(96)
        self._buttons_layout.addWidget(asset_tab)
        working_asset = QWidget()
        self._working_asset_layout = QHBoxLayout()
        self._working_asset_layout.setContentsMargins(0, 0, 0, 0)
        self._working_asset_layout.setSpacing(1)
        working_asset.setLayout(self._working_asset_layout)
        published_asset = QWidget()
        self._published_asset_layout = QHBoxLayout()
        self._published_asset_layout.setContentsMargins(0, 0, 0, 0)
        self._published_asset_layout.setSpacing(1)
        published_asset.setLayout(self._published_asset_layout)
        asset_tab.addTab(working_asset, 'Working')
        asset_tab.addTab(published_asset, 'Published')
        self._asset_published_info = solstice_published_info_widget.PublishedInfoWidget(asset=asset, check_versions=check_versions)
        self._asset_description = QTextEdit()
        self._asset_description.setReadOnly(True)
        self._publish_btn = QPushButton('> PUBLISH NEW VERSION <')

        main_layout.addWidget(self._asset_info_lbl)
        main_layout.addWidget(self._asset_icon)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addLayout(self._buttons_layout)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addWidget(self._asset_published_info)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addWidget(self._asset_description)
        main_layout.addWidget(self._publish_btn)


class AssetWidget(QWidget, object):

    sync_finished = Signal()

    def __init__(self, **kwargs):
        parent = kwargs['parent'] if 'parent' in kwargs else None
        super(AssetWidget, self).__init__(parent=parent)

        self._name = kwargs['name'] if 'name' in kwargs else 'New_Asset'
        self._asset_path = kwargs['path'] if 'path' in kwargs else None
        self._category = kwargs['category'] if 'category' in kwargs else None
        self._description = kwargs['description'] if 'description' in kwargs else ''
        self._icon_format = kwargs['icon_format'] if 'icon_format' in kwargs else None
        self._preview_format = kwargs['preview_format'] if 'preview_format' in kwargs else None
        self._simple_mode = kwargs['simple_mode'] if 'simple_mode' in kwargs else False
        self._checkable = kwargs['checkable'] if 'checkable' in kwargs else False
        self._icon = kwargs['icon'] if 'icon' in kwargs else None
        self._preview = kwargs['preview'] if 'preview' in kwargs else None
        self._menu = QMenu(self)
        if self._icon:
            self._icon = self._icon.encode('utf-8')
        if self._preview:
            self._preview = self._preview.encode('utf-8')

        self.setMaximumWidth(160)
        self.setMaximumHeight(200)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)
        self.setLayout(main_layout)

        self._asset_btn = QPushButton('', self)
        if self._icon:
            self._asset_btn.setIcon(QPixmap.fromImage(img.base64_to_image(self._icon, image_format=self._icon_format)))
            self._asset_btn.setIconSize(QSize(150, 150))

        self._asset_label = QLabel(self._name)
        self._asset_label.setAlignment(Qt.AlignCenter)
        for widget in [self._asset_btn, self._asset_label]:
            main_layout.addWidget(widget)

        self._asset_btn.setCheckable(self._checkable)

        self._asset_info = None

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def icon(self):
        return self._icon

    @property
    def icon_format(self):
        return self._icon_format

    @property
    def preview(self):
        return self._preview

    @property
    def preview_format(self):
        return self._preview_format

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def simple_mode(self):
        return self._simple_mode

    def print_asset_info(self):
        print('- {0}'.format(self._name))
        print('\t          Path: {0}'.format(self._asset_path))
        print('\t      Category: {0}'.format(self._category))
        print('\t   Description: {0}'.format(self._category))
        print('\t   Icon Format: {0}'.format(self._icon_format))
        print('\tPreview Format: {0}'.format(self._preview_format))
        print('\t   Simple Mode: {0}'.format(self._simple_mode))
        print('\t  Is Checkable: {0}'.format(self._checkable))

    def contextMenuEvent(self, event):
        self.generate_context_menu()
        if not self._menu:
            return
        self._menu.exec_(event.globalPos())

    def get_local_versions(self, status='published'):
        folders = ['model', 'textures', 'shading', 'groom']
        local_folders = dict()
        for f in folders:
            local_folders[f] = dict()

        for p in os.listdir(self._asset_path):
            if status == 'working':
                if p != '__working__':
                    continue

                for f in os.listdir(os.path.join(self._asset_path, '__working__')):
                    if f in folders:
                        asset_name = self._name
                        if f == 'shading':
                            asset_name = asset_name + '_SHD'
                        if f == 'textures':
                            continue

                        file_path = os.path.join(self._asset_path, '__working__', f, asset_name+'.ma')
                        history = artella.get_asset_history(file_path)
                        local_folders[f] = history
            else:
                if p == '__working__':
                    continue

                for f in folders:
                    if f in p:
                        version = sp.get_asset_version(p)[1]
                        local_folders[f][str(version)] = p

                # Sort all dictionaries by version number
                for f in folders:
                    local_folders[f] = collections.OrderedDict(sorted(local_folders[f].items()))

        return local_folders

    def get_published_versions(self):
        asset_data = list()
        thread, event = sp.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticePublishedInfo', self.get_artella_asset_data, [asset_data])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.25)
        if asset_data and len(asset_data) > 0:
            asset_data = asset_data[0]
            if not asset_data:
                return
            return asset_data.get_published_versions()

    def get_max_local_versions(self):
        folders = ['model', 'textures', 'shading', 'groom']
        max_local_versions = dict()
        for f in folders:
            max_local_versions[f] = None

        local_versions = self.get_local_versions()

        for f, versions in local_versions.items():
            if versions:
                for version, version_folder in versions.items():
                    if max_local_versions[f] is None:
                        max_local_versions[f] = [int(version), version_folder]
                    else:
                        if int(max_local_versions[f][0]) < int(version):
                            max_local_versions[f] = [int(version), version_folder]

        return max_local_versions

    def get_max_published_versions(self):
        folders = ['model', 'textures', 'shading', 'groom']
        max_server_versions = dict()
        for f in folders:
            max_server_versions[f] = None

        server_versions = self.get_published_versions()

        for f, versions in server_versions.items():
            if versions:
                for version, version_folder in versions.items():
                    if max_server_versions[f] is None:
                        max_server_versions[f] = [int(version), version_folder]
                    else:
                        if int(max_server_versions[f][0]) < int(version):
                            max_server_versions[f] = [int(version), version_folder]

        return max_server_versions

    def get_max_versions(self, status='published'):
        folders = ['model', 'textures', 'shading', 'groom']
        max_versions = dict()
        published_versions = self.get_published_versions()
        local_versions = self.get_local_versions(status=status)
        for t in ['local', 'server']:
            max_versions[t] = dict()
            for f in folders:
                max_versions[t][f] = None

        for(local_name, local_versions), (server_name, server_versions) in zip(local_versions.items(), published_versions.items()):
            if local_versions:
                for version, version_folder in local_versions.items():
                    if max_versions['local'][local_name] is None:
                        max_versions['local'][local_name] = int(version)
                    else:
                        if int(max_versions['local'][local_name]) < int(version):
                            max_versions['local'][local_name] = int(version)
            else:
                max_versions['local'][local_name] = None

            if server_versions:
                for version, version_folder in server_versions.items():
                    if max_versions['server'][server_name] is None:
                        max_versions['server'][server_name] = int(version)
                    else:
                        if int(max_versions['server'][server_name]) < int(version):
                            max_versions['server'][server_name] = int(version)
            else:
                max_versions['server'][server_name] = None

        return max_versions

    def is_published(self):
        asset_data = list()
        thread, event = sp.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticeAssetInfo', self.get_artella_asset_data, [asset_data])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.25)
        if asset_data and len(asset_data) > 0:
            asset_data = asset_data[0]
            if not asset_data:
                return
            published_in_server = asset_data.get_is_published()
            if published_in_server:
                sp.logger.debug('Asset {0} is published in Artella Server!'.format(self._name))

                # TODO: Update Info and check if our local version is the same as the
                # version located in Artella server

                return True

        sp.logger.debug('Asset {0} is not published in Artella Server!'.format(self._name))
        return False

    def get_artella_asset_data(self, thread_result=None, thread_event=None):
        rst = artella.get_status(os.path.join(self._asset_path))
        if thread_event:
            thread_event.set()
            thread_result.append(rst)
        return rst

    def generate_context_menu(self):
        """
        This class generates a context menu for the Asset widget depending of the asset
        widget properties
        :return: QMenu
        """
        self._menu = QMenu(self)
        self._menu.addAction('Open Asset in Light Rig')

        get_info_action = QAction('Get Info (DEV)', self._menu)
        self._menu.addAction(get_info_action)
        sync_action = QAction('Synchronize', self._menu)
        sync_menu = QMenu(self)
        sync_action.setMenu(sync_menu)
        sync_all_action = QAction('All', self._menu)
        sync_menu.addAction(sync_all_action)
        sync_menu.addSeparator()
        sync_model_action = QAction('Model', self._menu)
        sync_menu.addAction(sync_model_action)
        sync_textures_action = QAction('Textures', self._menu)
        sync_menu.addAction(sync_textures_action)
        sync_shading_action = QAction('Shading', self._menu)
        sync_menu.addAction(sync_shading_action)
        self._menu.addAction(sync_action)
        check_versions_action = QAction('Check for New Versions', self._menu)
        self._menu.addAction(check_versions_action)
        import_asset_action = QAction('Import to current scene ...', self._menu)
        self._menu.addAction(import_asset_action)
        reference_asset_action = QAction('Reference in current scene ...', self._menu)
        self._menu.addAction(reference_asset_action)

        get_info_action.triggered.connect(self.get_asset_info)
        sync_model_action.triggered.connect(partial(self.sync, 'model', False))
        sync_textures_action.triggered.connect(partial(self.sync, 'textures', False))
        sync_shading_action.triggered.connect(partial(self.sync, 'shading', False))

        if self.category == 'Characters':
            sync_menu_grooming_action = QAction('Groom', self._menu)
            sync_menu.addAction(sync_menu_grooming_action)
            sync_menu_grooming_action.triggered.connect(partial(self.sync, 'groom', False))


    def get_asset_info(self):
        rsp = artella.get_status(self._asset_path, as_json=True)
        print(rsp)

    def sync(self, sync_type='all', ask=False):

        if sync_type != 'all' and sync_type != 'model' and sync_type != 'shading' and sync_type != 'textures':
            sp.logger.error('Synchronization type {0} is not valid!'.format(sync_type))
            return

        if ask:
            result = solstice_qt_utils.show_question(None, 'Synchronize file {0}'.format(self._name), 'Are you sure you want to synchronize this asset? This can take quite a lot of time!')
            if result == QMessageBox.No:
                return

        start_time = time.time()

        if sync_type == 'all':
            paths_to_sync = [self._asset_path, os.path.join(self._asset_path, '__working__')]
        else:
            paths_to_sync = [os.path.join(self._asset_path, '__working__', sync_type)]

        max_versions = self.get_max_published_versions()
        for f, version_list in max_versions.items():
            if not version_list:
                continue
            version_type = version_list[1]
            if sync_type != 'all':
                if sync_type in version_type:
                    paths_to_sync.append(os.path.join(self._asset_path, '__{0}__'.format(version_list[1])))
            else:
                paths_to_sync.append(os.path.join(self._asset_path, '__{0}__'.format(version_list[1])))

        solstice_sync_dialog.SolsticeSyncFile(files=paths_to_sync).sync()
        elapsed_time = time.time() - start_time
        sp.logger.debug('{0} synchronized in {1} seconds'.format(self._name, elapsed_time))
        self.sync_finished.emit()

    def open_asset_file(self, file_type, status):
        if file_type != 'model' and file_type != 'textures' and file_type != 'shading' and file_type != 'shading':
            return
        if status != 'working' and status != 'published':
            return
        asset_name = self._name
        if file_type == 'shading':
            asset_name = self._name + '_SHD'
        elif file_type == 'groom':
            asset_name = self._name + '_GROOMING'
        asset_name = asset_name + '.ma'

        if status == 'working':
            working_path = os.path.join(self._asset_path, '__working__', file_type, asset_name)
            if os.path.isfile(working_path):
                artella.open_file_in_maya(file_path=working_path)
        elif status == 'published':
            local_max_versions = self.get_max_local_versions()
            if local_max_versions[file_type]:
                published_path = os.path.join(self._asset_path, local_max_versions[file_type][1], file_type, asset_name)
                if os.path.isfile(published_path):
                    artella.open_file_in_maya(file_path=published_path)

    def open_textures_folder(self, status):
        if status != 'working' and status != 'published':
            return
        if status == 'working':
            working_path = os.path.join(self._asset_path, '__working__', 'textures')
            if os.path.exists(working_path):
                solstice_python_utils.open_folder(working_path)
        elif status == 'published':
            local_max_versions = self.get_max_local_versions()
            if local_max_versions['textures']:
                published_path = os.path.join(self._asset_path, local_max_versions['textures'][1], 'textures')
                if os.path.exists(published_path):
                    solstice_python_utils.open_folder(published_path)

    def generate_asset_info_widget(self, check_versions=False):
        self._asset_info = AssetInfo(asset=self, check_versions=check_versions)
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._sync_btn = QPushButton('Sync')
        self._check_btn = QPushButton('Check')
        for btn in [self._folder_btn, self._artella_btn, self._sync_btn, self._check_btn]:
            self._asset_info._asset_buttons_layout.addWidget(btn)

        self._working_model_btn = QPushButton('Model')
        self._working_shading_btn = QPushButton('Shading')
        self._working_textures_btn = QPushButton('Textures')
        self._published_model_btn = QPushButton('Model')
        self._published_shading_btn = QPushButton('Shading')
        self._published_textures_btn = QPushButton('Textures')
        for btn in [self._working_model_btn, self._working_shading_btn, self._working_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._working_asset_layout.addWidget(btn)
        for btn in [self._published_model_btn, self._published_shading_btn, self._published_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._published_asset_layout.addWidget(btn)
        self.update_asset_info()

        self._folder_btn.clicked.connect(partial(artella.explore_file, self._asset_path))
        self._artella_btn.clicked.connect(self.open_asset_artella_url)
        self._sync_btn.clicked.connect(self.sync)
        self._check_btn.clicked.connect(self.sync_finished.emit)
        self._working_model_btn.clicked.connect(partial(self.open_asset_file, 'model', 'working'))
        self._working_shading_btn.clicked.connect(partial(self.open_asset_file, 'shading', 'working'))
        self._working_textures_btn.clicked.connect(partial(self.open_textures_folder, 'working'))
        self._published_model_btn.clicked.connect(partial(self.open_asset_file, 'model', 'published'))
        self._published_shading_btn.clicked.connect(partial(self.open_asset_file, 'shading', 'published'))
        self._published_textures_btn.clicked.connect(partial(self.open_textures_folder, 'published'))

    def open_asset_artella_url(self):

        file_path = os.path.relpath(self._asset_path, sp.get_solstice_assets_path())
        asset_url = 'https://www.artella.com/project/{0}/files/Assets/{1}'.format(sp.solstice_project_id_raw, file_path)
        webbrowser.open(asset_url)

    def get_asset_info_widget(self, check_versions=False):
        self.generate_asset_info_widget(check_versions=check_versions)
        return self._asset_info

    def update_asset_info(self):
        if not self._asset_info:
            return

        self._asset_info._asset_info_lbl.set_text(self._name.upper())
        if self._icon is not None and self._icon != '':
            self._asset_info._asset_icon.setPixmap(QPixmap.fromImage(img.base64_to_image(self._icon, image_format=self._icon_format)).scaled(300, 300, Qt.KeepAspectRatio))
        self._asset_info._asset_description.setText(self._description)


class CharacterAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(CharacterAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_versions=False):
        super(CharacterAsset, self).generate_asset_info_widget(check_versions=check_versions)
        if not self._asset_info:
            return

        self._working_groom_btn = QPushButton('Groom')
        self._published_groom_btn = QPushButton('Groom')
        self._working_groom_btn.clicked.connect(partial(self.open_asset_file, 'groom', 'working'))
        self._published_groom_btn.clicked.connect(partial(self.open_asset_file, 'groom', 'pubilshed'))

    def update_asset_info(self):
        super(CharacterAsset, self).update_asset_info()


class PropAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(PropAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_versions=False):
        super(PropAsset, self).generate_asset_info_widget(check_versions=check_versions)

    def update_asset_info(self):
        super(PropAsset, self).update_asset_info()


class BackgroundElementAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(BackgroundElementAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_versions=False):
        super(BackgroundElementAsset, self).generate_asset_info_widget(check_versions=check_versions)

    def update_asset_info(self):
        super(BackgroundElementAsset, self).update_asset_info()
