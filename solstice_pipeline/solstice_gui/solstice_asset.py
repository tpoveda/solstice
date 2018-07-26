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

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_utils import solstice_image as img
from solstice_utils import solstice_artella_utils as artella
from solstice_utils import solstice_artella_classes, solstice_qt_utils, solstice_python_utils
from solstice_gui import solstice_splitters, solstice_published_info_widget, solstice_sync_dialog, solstice_buttons
from solstice_tools import solstice_publisher
from resources import solstice_resource

reload(img)
reload(artella)
reload(solstice_artella_classes)
reload(solstice_qt_utils)
reload(solstice_python_utils)
reload(solstice_splitters)
reload(solstice_published_info_widget)
reload(solstice_sync_dialog)
reload(solstice_buttons)
reload(solstice_resource)
reload(solstice_publisher)

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

    def __init__(self, asset, check_published_info=False, check_working_info=False, check_lock_info=False):
        super(AssetInfo, self).__init__()

        self._check_published_info = check_published_info
        self._check_working_info = check_working_info
        self._check_lock_info = check_lock_info

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.setAlignment(Qt.AlignTop)
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
        self.asset_tab = QTabWidget()
        self.asset_tab.setMinimumHeight(80)
        self._buttons_layout.addWidget(self.asset_tab)
        self.working_asset = QWidget()
        self._working_asset_layout = QHBoxLayout()
        self._working_asset_layout.setContentsMargins(0, 0, 0, 0)
        self._working_asset_layout.setSpacing(1)
        self.working_asset.setLayout(self._working_asset_layout)
        self.published_asset = QWidget()
        self._published_asset_layout = QHBoxLayout()
        self._published_asset_layout.setContentsMargins(0, 0, 0, 0)
        self._published_asset_layout.setSpacing(1)
        self.published_asset.setLayout(self._published_asset_layout)
        self.asset_tab.addTab(self.working_asset, 'Working')
        self.asset_tab.addTab(self.published_asset, 'Published')
        self._asset_published_info = solstice_published_info_widget.PublishedInfoWidget(asset=asset, check_published_info=check_published_info, check_working_info=check_working_info)

        self._bottom_layout = QHBoxLayout()
        self._publish_btn = QPushButton('> PUBLISH NEW VERSION <')
        self._new_working_version_btn = QPushButton('> NEW WORKING VERSION <')
        self._bottom_layout.addWidget(self._publish_btn)
        self._bottom_layout.addWidget(self._new_working_version_btn)

        self._publish_btn.clicked.connect(asset.publish)
        self._new_working_version_btn.clicked.connect(asset.new_version)

        main_layout.addWidget(self._asset_info_lbl)
        main_layout.addWidget(self._asset_icon)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addLayout(self._buttons_layout)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addWidget(self._asset_published_info)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addLayout(self._bottom_layout)
        main_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        # Uncomment if you want to check for locked/unlocked files each time
        # the user presses Working/Published tabs
        # self.asset_tab.currentChanged.connect(self.update_buttons)

    def update_buttons(self, index):
        widgets = list()
        if index == 0:
            widgets = self.working_asset.findChildren(solstice_buttons.CategoryButtonWidget)
        elif index == 1:
            widgets = self.published_asset.findChildren(solstice_buttons.CategoryButtonWidget)
        for w in widgets:
            w.update()


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
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(2, 2, 2, 2)
        widget_layout.setSpacing(0)
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        main_frame.setLineWidth(1)
        main_frame.setLayout(widget_layout)
        main_layout.addWidget(main_frame)

        self._asset_btn = QPushButton('', self)
        if self._icon:
            self._asset_btn.setIcon(QPixmap.fromImage(img.base64_to_image(self._icon, image_format=self._icon_format)))
            self._asset_btn.setIconSize(QSize(150, 150))

        self._asset_label = QLabel(self._name)
        self._asset_label.setStyleSheet("background-color:rgba(0, 0, 0, 150);")
        self._asset_label.setAlignment(Qt.AlignCenter)
        for widget in [self._asset_btn, self._asset_label]:
            widget_layout.addWidget(widget)
        self._asset_btn.setCheckable(self._checkable)

        self._asset_info = None

    @property
    def name(self):
        return self._name

    @property
    def asset_path(self):
        return self._asset_path

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

    def publish(self):
        solstice_publisher.run(asset=self)

    def new_version(self):
        solstice_publisher.run(asset=self, new_working_version=True)

    def contextMenuEvent(self, event):
        if not self._simple_mode:
            self.generate_context_menu()
            if not self._menu:
                return
            self._menu.exec_(event.globalPos())

    def get_local_versions(self, status='published', categories=None):

        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        local_folders = dict()
        for f in folders:
            local_folders[f] = dict()

        for p in os.listdir(self._asset_path):
            if status == 'working':
                if p != '__working__':
                    continue

                for f in os.listdir(os.path.join(self._asset_path, '__working__')):
                    if f in folders:
                        if f == 'textures':
                            # In textures we can have multiple textures files with different versions each one
                            txt_files = list()
                            for (dir_path, dir_names, file_names) in os.walk(os.path.join(self._asset_path, '__working__', f)):
                                txt_files.extend(file_names)
                                break

                            textures_history = dict()
                            if len(txt_files) > 0:
                                for txt in txt_files:
                                    txt_path = os.path.join(self._asset_path, '__working__', f, txt)
                                    txt_history = artella.get_asset_history(txt_path)
                                    textures_history[txt] = txt_history
                            local_folders[f] = textures_history
                        else:
                            asset_name = self._name
                            if f == 'shading':
                                asset_name = asset_name + '_SHD'
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

                # Sort all dictionaries by version number when we are getting published version info
                for f in folders:
                    local_folders[f] = collections.OrderedDict(sorted(local_folders[f].items()))

        return local_folders

    def get_server_versions(self, status='published', all_versions=False, categories=None):
        if status == 'published':
            asset_data = list()
            thread, event = sp.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticePublishedInfo', self.get_artella_asset_data, [asset_data])
            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.25)
            if asset_data and len(asset_data) > 0:
                asset_data = asset_data[0]
                if not asset_data:
                    return

            published_versions = asset_data.get_published_versions(all=all_versions)
            if categories:
                publish_dict = dict()
                for cat in categories:
                    if cat in published_versions.keys():
                        publish_dict[cat] = published_versions[cat]
                return publish_dict

            return published_versions
        else:
            server_data = dict()

            if categories:
                if type(categories) not in [list]:
                    folders = [categories]
                else:
                    folders = categories
            else:
                folders = sp.valid_categories

            for category in folders:
                server_data[category] = dict()
                server_path = os.path.join(self._asset_path, '__working__', category)

                asset_data = list()
                thread, event = sp.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticePublishedInfo', self.get_artella_asset_data_path, [server_path, asset_data])
                while not event.is_set():
                    QCoreApplication.processEvents()
                    event.wait(0.25)
                if asset_data and len(asset_data) > 0:
                    asset_data = asset_data[0]
                    if not asset_data:
                        return
                try:
                    for ref_name, ref_data in asset_data.references.items():
                        if category == 'textures':
                            ref_path = os.path.join(server_path, ref_data.name)

                            # TODO: Create custom sync dialog

                            ref_history = artella.get_asset_history(ref_path)
                            server_data[category][ref_data.name] = ref_history
                        else:
                            ref_path = os.path.join(server_path, ref_data.name)

                            # TODO: Create custom sync dialog

                            if os.path.isfile(ref_path):
                                ref_history = artella.get_asset_history(ref_path)
                                server_data[category] = ref_history
                except Exception:
                    # This exception si launched if some server folder has no valid files. For example, if an asset
                    # does not have a grooming file. In those cases the server version data for that category is {}
                    if not server_data[category]:
                        server_data[category] = {}
            return server_data

    def get_max_local_versions(self, categories=None):

        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

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

    def get_max_published_versions(self, all_versions=False, categories=None):
        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        max_server_versions = dict()
        for f in folders:
            max_server_versions[f] = None

        server_versions = self.get_server_versions(all_versions=all_versions)

        for f, versions in server_versions.items():
            if versions:
                for version, version_folder in versions.items():
                    if max_server_versions[f] is None:
                        max_server_versions[f] = [int(version), version_folder]
                    else:
                        if int(max_server_versions[f][0]) < int(version):
                            max_server_versions[f] = [int(version), version_folder]

        return max_server_versions

    def get_max_working_versions(self, all_versions=False, categories=None):
        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        max_server_versions = dict()
        for f in folders:
            max_server_versions[f] = None

        server_versions = self.get_server_versions(all_versions=all_versions, status='working')

        for f, versions in server_versions.items():
            if f == 'textures':
                pass
            else:
                if not versions:
                    continue
                file_versions = versions.versions
                for v in file_versions:
                    if max_server_versions[f] is None:
                        max_server_versions[f] = [int(v[0]), v[1].relative_path]
                    else:
                        if int(max_server_versions[f][0]) < int(v[0]):
                            max_server_versions[f] = [int(v[0]), v[1].relative_path]

        return max_server_versions

    def get_max_versions(self, status='published', categories=None):

        if categories:
            if type(categories) not in [list]:
                folders = [categories]
            else:
                folders = categories
        else:
            folders = sp.valid_categories

        max_versions = dict()
        server_versions_list = self.get_server_versions(status=status, categories=folders)
        local_versions_list = self.get_local_versions(status=status, categories=folders)
        for t in ['local', 'server']:
            max_versions[t] = dict()
            for f in folders:
                max_versions[t][f] = None

        for(local_name, local_versions), (server_name, server_versions) in zip(local_versions_list.items(), server_versions_list.items()):
            if local_versions:
                if status == 'published':
                    for version, version_folder in local_versions.items():
                        if max_versions['local'][local_name] is None:
                            max_versions['local'][local_name] = int(version)
                        else:
                            if int(max_versions['local'][local_name]) < int(version):
                                max_versions['local'][local_name] = int(version)
                else:
                    if local_name == 'textures':
                        max_versions['local'][local_name] = dict()
                        for txt, txt_data in local_versions.items():
                            for v in txt_data.versions:
                                if txt not in max_versions['local'][local_name]:
                                    max_versions['local'][local_name][txt] = v[1]
                                else:
                                    if int(max_versions['local'][local_name][txt].version) < int(v[1].version):
                                        max_versions['local'][local_name][txt] = v[1]
                    else:
                        for v in local_versions.versions:
                            if max_versions['local'][local_name] is None:
                                max_versions['local'][local_name] = v[1]
                            else:
                                if int(max_versions['local'][local_name].version) < int(v[1].version):
                                    max_versions['local'][local_name] = v[1]
            else:
                max_versions['local'][local_name] = None

            if server_versions:
                if status == 'published':
                    for version, version_folder in server_versions.items():
                        if max_versions['server'][server_name] is None:
                            max_versions['server'][server_name] = int(version)
                        else:
                            if int(max_versions['server'][server_name]) < int(version):
                                max_versions['server'][server_name] = int(version)
                else:
                    if local_name == 'textures':
                        max_versions['server'][local_name] = dict()
                        for txt, txt_data in server_versions.items():
                            for v in txt_data.versions:
                                if txt not in max_versions['server'][local_name]:
                                    max_versions['server'][local_name][txt] = v[1]
                                else:
                                    if int(max_versions['server'][local_name][txt].version) < int(v[1].version):
                                        max_versions['server'][local_name][txt] = v[1]
                    else:
                        for v in server_versions.versions:
                            if max_versions['server'][local_name] is None:
                                max_versions['server'][local_name] = v[1]
                            else:
                                if int(max_versions['server'][local_name].version) < int(v[1].version):
                                    max_versions['server'][local_name] = v[1]
            else:
                max_versions['server'][server_name] = None

        return max_versions

    def lock(self, category, status='working'):
        versions = self.get_max_versions(status=status, categories=category)
        if versions['server']:
            if versions['server'][category]:
                if category == 'textures':
                    if status == 'working':
                        for txt_name, txt_data in versions['server'][category].items():
                            file_path = os.path.join(self.asset_path, '__working__', txt_data.relative_path)
                            artella.lock_asset(file_path=file_path)
                else:
                    if status == 'working':
                        file_path = os.path.join(self.asset_path, '__working__', versions['server'][category].relative_path)
                        artella.lock_asset(file_path=file_path)

    def unlock(self, category, status='working'):
        versions = self.get_max_versions(status=status, categories=category)
        if versions['server']:
            if category == 'textures':
                if status == 'working':
                    for txt_name, txt_data in versions['server'][category].items():
                        file_path = os.path.join(self.asset_path, '__working__', txt_data.relative_path)
                        artella.unlock_asset(file_path=file_path)
            else:
                if status == 'working':
                    file_path = os.path.join(self.asset_path, '__working__', versions['server'][category].relative_path)
                    artella.unlock_asset(file_path=file_path)

    def is_locked(self, category, status='working'):
        versions = self.get_max_versions(status=status, categories=category)
        if versions['server']:
            if versions['server'][category]:
                if category == 'textures':
                    for txt_data in versions['server'][category].items():
                        if status == 'working':
                            file_path = os.path.join(self.asset_path, '__working__', 'textures', txt_data[0])
                        else:
                            file_path = os.path.join(self.asset_path, 'textures', txt_data[0])
                        current_user_can_unlock = artella.can_unlock(file_path=file_path)
                        if txt_data[1].locked_by is not None:
                            return True, current_user_can_unlock
                        else:
                            return False, current_user_can_unlock
                else:
                    if status == 'working':
                        file_path = os.path.join(self.asset_path, '__working__', versions['server'][category].relative_path)
                    else:
                        file_path = os.path.join(self.asset_path, '__{0}_v{1}__'.format(category, '{0:03}'.format(versions['server'][category])))

                    current_user_can_unlock = artella.can_unlock(file_path=file_path)
                    locked_by = versions['server'][category].locked_by

                    return locked_by, current_user_can_unlock

        return False, False

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

    def get_artella_asset_data_path(self, path, thread_result=None, thread_event=None):
        rst = artella.get_status(path)
        if thread_event:
            thread_event.set()
            thread_result.append(rst)
        return rst

    def get_artella_asset_history(self, path, thread_result=None, thread_event=None):
        rst = artella.get_asset_history(path)
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
        sync_all_action.triggered.connect(partial(self.sync, 'all', False))
        sync_model_action.triggered.connect(partial(self.sync, 'model', False))
        sync_textures_action.triggered.connect(partial(self.sync, 'textures', False))
        sync_shading_action.triggered.connect(partial(self.sync, 'shading', False))
        import_asset_action.triggered.connect(self.import_asset_file)
        reference_asset_action.triggered.connect(self.reference_asset_file)

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
                    paths_to_sync.append(os.path.join(self._asset_path, '{0}'.format(version_list[1])))
            else:
                paths_to_sync.append(os.path.join(self._asset_path, '{0}'.format(version_list[1])))

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

    def import_asset_file(self):
        asset_name = self._name + '.ma'
        local_max_versions = self.get_max_local_versions()
        if local_max_versions['model']:
            published_path = os.path.join(self._asset_path, local_max_versions['model'][1], 'model', asset_name)
            if os.path.isfile(published_path):
                artella.import_file_in_maya(file_path=published_path)

    def reference_asset_file(self):
        asset_name = self._name + '.ma'
        local_max_versions = self.get_max_local_versions()
        if local_max_versions['model']:
            published_path = os.path.join(self._asset_path, local_max_versions['model'][1], 'model', asset_name)
            if os.path.isfile(published_path):
                artella.reference_file_in_maya(file_path=published_path)

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

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        self._asset_info = AssetInfo(asset=self, check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._check_btn = QPushButton('Check')
        for btn in [self._folder_btn, self._artella_btn, self._check_btn]:
            self._asset_info._asset_buttons_layout.addWidget(btn)

        # Create buttons for assets files
        self._working_model_btn = solstice_buttons.CategoryButtonWidget(category_name='Model', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_shading_btn = solstice_buttons.CategoryButtonWidget(category_name='Shading', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_textures_btn = solstice_buttons.CategoryButtonWidget(category_name='Textures', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_model_btn = solstice_buttons.CategoryButtonWidget(category_name='Model', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_shading_btn = solstice_buttons.CategoryButtonWidget(category_name='Shading', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_textures_btn = solstice_buttons.CategoryButtonWidget(category_name='Textures', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)

        for btn in [self._working_model_btn, self._working_shading_btn, self._working_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._working_asset_layout.addWidget(btn)
        for btn in [self._published_model_btn, self._published_shading_btn, self._published_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._published_asset_layout.addWidget(btn)

        self.update_asset_info()

        self._folder_btn.clicked.connect(partial(artella.explore_file, self._asset_path))
        self._artella_btn.clicked.connect(self.open_asset_artella_url)
        self._check_btn.clicked.connect(self.sync_finished.emit)

    def open_asset_artella_url(self):

        file_path = os.path.relpath(self._asset_path, sp.get_solstice_assets_path())
        asset_url = 'https://www.artella.com/project/{0}/files/Assets/{1}'.format(sp.solstice_project_id_raw, file_path)
        webbrowser.open(asset_url)

    def get_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        self.generate_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
        return self._asset_info

    def update_asset_info(self):
        if not self._asset_info:
            return

        self._asset_info._asset_info_lbl.set_text(self._name.upper())
        if self._icon is not None and self._icon != '':
            self._asset_info._asset_icon.setPixmap(QPixmap.fromImage(img.base64_to_image(self._icon, image_format=self._icon_format)).scaled(300, 300, Qt.KeepAspectRatio))
        self._asset_info._asset_published_info._asset_description.setText(self._description)

    def has_model(self):
        return True

    def has_shading(self):
        return True

    def has_textures(self):
        return True

    def has_groom(self):
        return False

    def has_category(self, category):
        if category == 'model':
            return self.has_model()
        if category == 'shading':
            return self.has_shading()
        if category == 'textures':
            return self.has_textures()
        if category == 'groom':
            return self.has_groom()


class CharacterAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(CharacterAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        super(CharacterAsset, self).generate_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
        if not self._asset_info:
            return

        self._working_groom_btn = solstice_buttons.CategoryButtonWidget(category_name='Groom', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_groom_btn = solstice_buttons.CategoryButtonWidget(category_name='Groom', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)

    def has_groom(self):
        return True

    def update_asset_info(self):
        super(CharacterAsset, self).update_asset_info()


class PropAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(PropAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        super(PropAsset, self).generate_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)

    def update_asset_info(self):
        super(PropAsset, self).update_asset_info()


class BackgroundElementAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(BackgroundElementAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        super(BackgroundElementAsset, self).generate_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)

    def update_asset_info(self):
        super(BackgroundElementAsset, self).update_asset_info()
