#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import time
import weakref
import importlib
import webbrowser
from functools import partial
from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.core import syncdialog, node
from solstice.pipeline.gui import splitters, buttons
from solstice.pipeline.utils import qtutils, pythonutils, image as img, artellautils as artella, namingutils as naming
from solstice.pipeline.resources import resource

from solstice.pipeline.tools.pipelinizer import publisher
from solstice.pipeline.tools.alembicmanager import alembicmanager

if sp.is_maya():
    from solstice.pipeline.tools.standinmanager import standinmanager
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary


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

        self._asset_info_lbl = splitters.Splitter(asset.name)
        self._asset_icon = QLabel()
        self._asset_icon.setPixmap(resource.pixmap('empty_file', category='icons').scaled(200, 200, Qt.KeepAspectRatio))
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
        self._asset_published_info = PublishedInfoWidget(asset=asset, check_published_info=check_published_info, check_working_info=check_working_info)

        self._bottom_layout = QHBoxLayout()
        self._publish_btn = QPushButton('> PUBLISH NEW VERSION <')
        self._new_working_version_btn = QPushButton('> NEW WORKING VERSION <')
        self._bottom_layout.addWidget(self._publish_btn)
        self._bottom_layout.addWidget(self._new_working_version_btn)

        self._publish_btn.clicked.connect(asset.publish)
        self._new_working_version_btn.clicked.connect(asset.new_version)

        main_layout.addWidget(self._asset_info_lbl)
        main_layout.addWidget(self._asset_icon)
        main_layout.addLayout(splitters.SplitterLayout())
        main_layout.addLayout(self._buttons_layout)
        main_layout.addLayout(splitters.SplitterLayout())
        main_layout.addWidget(self._asset_published_info)
        main_layout.addLayout(splitters.SplitterLayout())
        main_layout.addLayout(self._bottom_layout)
        main_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        # Uncomment if you want to check for locked/unlocked files each time
        # the user presses Working/Published tabs
        # self.asset_tab.currentChanged.connect(self.update_buttons)

    def update_buttons(self, index):
        widgets = list()
        if index == 0:
            widgets = self.working_asset.findChildren(buttons.CategoryButtonWidget)
        elif index == 1:
            widgets = self.published_asset.findChildren(buttons.CategoryButtonWidget)
        for w in widgets:
            w.update()


class AssetWidget(QWidget, node.SolsticeAssetNode):

    syncFinished = Signal()
    publishFinished = Signal()
    newVersionFinished = Signal()

    def __init__(self, **kwargs):
        parent = kwargs['parent'] if 'parent' in kwargs else None

        QWidget.__init__(self, parent=parent)
        node.SolsticeAssetNode.__init__(self, **kwargs)

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
    def simple_mode(self):
        return self._simple_mode

    # def print_asset_info(self):
    #     print('- {0}'.format(self._name))
    #     print('\t   Icon Format: {0}'.format(self._icon_format))
    #     print('\tPreview Format: {0}'.format(self._preview_format))
    #     print('\t   Simple Mode: {0}'.format(self._simple_mode))
    #     print('\t  Is Checkable: {0}'.format(self._checkable))

    def publish(self):
        result = publisher.run(asset=self)
        if result:
            self.publishFinished.emit()

    def new_version(self):
        result = publisher.run(asset=self, new_working_version=True)
        if result:
            self.newVersionFinished.emit()

    def contextMenuEvent(self, event):
        if not self._simple_mode:
            self.generate_context_menu()
            if not self._menu:
                return
            self._menu.exec_(event.globalPos())

    def get_server_versions(self, status='published', all_versions=False, categories=None):
        if status == 'published':
            asset_data = list()
            thread, event = sys.solstice.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticePublishedInfo', self.get_artella_asset_data, [asset_data])
            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.05)
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
                thread, event = sys.solstice.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticePublishedInfo', self.get_artella_asset_data_path, [server_path, asset_data])
                while not event.is_set():
                    QCoreApplication.processEvents()
                    event.wait(0.05)
                if asset_data and len(asset_data) > 0:
                    asset_data = asset_data[0]
                    if not asset_data:
                        return
                try:
                    for ref_name, ref_data in asset_data.references.items():
                        if category == 'textures':
                            # TODO: Create custom sync dialog
                            ref_path = os.path.join(server_path, ref_data.name)
                            ref_history = artella.get_asset_history(ref_path)
                            server_data[category][ref_data.name] = ref_history
                        elif category == 'shading':
                            ref_path = os.path.join(server_path, ref_data.name)
                            file_name = os.path.basename(ref_path)
                            if os.path.isfile(ref_path):
                                if file_name == '{}_SHD.ma'.format(self.name) or file_name == '{}_shd.ma'.format(self.name):
                                    ref_history = artella.get_asset_history(ref_path)
                                    server_data[category] = ref_history
                        elif category == 'groom':
                            ref_path = os.path.join(server_path, ref_data.name)
                            file_name = os.path.basename(ref_path)
                            if os.path.isfile(ref_path):
                                if file_name == '{}_GROOMING.ma'.format(self.name) or file_name == '{}_grooming.ma'.format(self.name):
                                    ref_history = artella.get_asset_history(ref_path)
                                    server_data[category] = ref_history
                        else:
                            # TODO: Create custom sync dialog
                            ref_path = os.path.join(server_path, ref_data.name)
                            file_name = os.path.basename(ref_path)
                            if os.path.isfile(ref_path) and file_name == '{}.ma'.format(self.name):
                                ref_history = artella.get_asset_history(ref_path)
                                server_data[category] = ref_history
                except Exception:
                    # This exception si launched if some server folder has no valid files. For example, if an asset
                    # does not have a grooming file. In those cases the server version data for that category is {}
                    if not server_data[category]:
                        server_data[category] = {}
            return server_data

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

        max_versions = OrderedDict()
        server_versions_list = self.get_server_versions(status=status, categories=folders)
        local_versions_list = self.get_local_versions(status=status, categories=folders)
        for t in ['local', 'server']:
            max_versions[t] = OrderedDict()
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
                        max_versions['local'][local_name] = OrderedDict()
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
                        max_versions['server'][local_name] = OrderedDict()
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
                            artella.lock_file(file_path=file_path, force=True)
                else:
                    if status == 'working':
                        file_path = os.path.join(self.asset_path, '__working__', versions['server'][category].relative_path)
                        artella.lock_file(file_path=file_path, force=True)

    def unlock(self, category, status='working'):
        versions = self.get_max_versions(status=status, categories=category)
        if versions['server']:
            if category == 'textures':
                if status == 'working':
                    for txt_name, txt_data in versions['server'][category].items():
                        file_path = os.path.join(self.asset_path, '__working__', txt_data.relative_path)
                        artella.unlock_file(file_path=file_path)
            else:
                if status == 'working':
                    file_path = os.path.join(self.asset_path, '__working__', versions['server'][category].relative_path)
                    artella.unlock_file(file_path=file_path)

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
        thread, event = sys.solstice.info_dialog.do('Checking {0} Asset Info'.format(self._name), 'SolsticeAssetInfo', self.get_artella_asset_data, [asset_data])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.05)
        if asset_data and len(asset_data) > 0:
            asset_data = asset_data[0]
            if not asset_data:
                return
            published_in_server = asset_data.get_is_published()
            if published_in_server:
                sys.solstice.logger.debug('Asset {0} is published in Artella Server!'.format(self._name))
                return True
        sys.solstice.logger.debug('Asset {0} is not published in Artella Server!'.format(self._name))
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

    def get_asset_textures(self, status='working', force_sync=False):
        """
        Returns a dict of textures with the given status
        :param status: str
        :return: dict<str, str>
        """

        published_textures_info = self.get_max_versions(status='published', categories=['textures'])['server']
        textures_version = published_textures_info['textures']
        current_textures = list()

        # The first time we publish textures, the path of the textures'll point to the work in progress textures
        if textures_version == 0:
            textures_path = os.path.join(self.asset_path, '__working__', 'textures')
            if os.path.exists(textures_path):
                textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
                for txt in textures:
                    fixed_txt = artella.fix_path_by_project(txt, fullpath=True)
                    format_txt = naming.format_path(fixed_txt)
                    current_textures.append(format_txt)
        else:
            textures_version = '{0:03}'.format(published_textures_info['textures'])
            textures_path = os.path.join(self.asset_path, '__textures_v{0}__'.format(textures_version))
            if not os.path.exists(textures_path) or force_sync:
                syncdialog.SolsticeSyncFile(files=[textures_path]).sync()
            if os.path.exists(textures_path):
                textures_path = os.path.join(textures_path, 'textures')
                if os.path.exists(textures_path):
                    textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
                    for txt in textures:
                        fixed_txt = artella.fix_path_by_project(txt, fullpath=True)
                        format_txt = naming.format_path(fixed_txt)
                        current_textures.append(format_txt)
            else:
                sys.solstice.logger.warning('Published textures path {} does not exists! Impossible to update texture paths ...'.format(textures_path))

        return current_textures

    def get_next_version_textures_paths(self):
        """
        Returns a dict with the current textures and other with the next version textures paths
        :param status: str
        :return: dict<str, str>, dict<str, str>
        """

        published_textures_info = self.get_max_versions(status='published', categories=['textures'])['server']
        textures_version = published_textures_info['textures']
        current_textures = list()

        # The first time we publish textures, the path of the textures'll point to the work in progress textures
        if textures_version == 0:
            textures_path = os.path.join(self.asset_path, '__working__', 'textures')
            if os.path.exists(textures_path):
                textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
                for txt in textures:
                    fixed_txt = artella.fix_path_by_project(txt, fullpath=True)
                    format_txt = naming.format_path(fixed_txt)
                    current_textures.append(format_txt)
        else:
            textures_version_full = '{0:03}'.format(published_textures_info['textures'])
            textures_path = os.path.join(self.asset_path, '__textures_v{0}__'.format(textures_version_full))
            if os.path.exists(textures_path):
                textures_path = os.path.join(textures_path, 'textures')
                if os.path.exists(textures_path):
                    textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
                    for txt in textures:
                        fixed_txt = artella.fix_path_by_project(txt, fullpath=True)
                        format_txt = naming.format_path(fixed_txt)
                        current_textures.append(format_txt)

        new_textures = list()
        textures_version_old = '{0:03}'.format(published_textures_info['textures'])
        textures_version_new = '{0:03}'.format(published_textures_info['textures']+1)
        for txt in current_textures:
            new_textures.append(txt.replace(textures_version_old, textures_version_new))

        return current_textures, new_textures

    def generate_context_menu(self):
        """
        This class generates a context menu for the Asset widget depending of the asset
        widget properties
        :return: QMenu
        """
        self._menu = QMenu(self)
        # get_info_action = QAction('Get Info (DEV)', self._menu)
        # self._menu.addAction(get_info_action)
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
        sync_rig_action = QAction('Rig', self._menu)
        sync_menu.addAction(sync_rig_action)
        # check_versions_action = QAction('Check for New Versions', self._menu)
        # self._menu.addAction(check_versions_action)
        import_asset_action = QAction('Import to current scene ...', self._menu)
        self._menu.addAction(import_asset_action)
        reference_asset_action = QAction('Reference in current scene ...', self._menu)
        self._menu.addAction(reference_asset_action)

        # get_info_action.triggered.connect(self.get_asset_info)
        sync_all_action.triggered.connect(partial(self.sync, 'all', 'all', False))
        sync_model_action.triggered.connect(partial(self.sync, 'model', 'all', False))
        sync_textures_action.triggered.connect(partial(self.sync, 'textures', 'all', False))
        sync_shading_action.triggered.connect(partial(self.sync, 'shading', 'all', False))
        sync_rig_action.triggered.connect(partial(self.sync, 'rig', 'all', False))
        import_asset_action.triggered.connect(self.import_model_file)
        reference_asset_action.triggered.connect(self.reference_asset_file)

        if self.category == 'Characters':
            sync_menu_grooming_action = QAction('Groom', self._menu)
            sync_menu.addAction(sync_menu_grooming_action)
            sync_menu_grooming_action.triggered.connect(partial(self.sync, 'groom', False))

    def get_asset_info(self):
        rsp = artella.get_status(self._asset_path, as_json=True)
        print(rsp)

    def sync(self, sync_type='all', status='all', ask=False):

        if sync_type != 'all' and sync_type != 'model' and sync_type != 'shading' and sync_type != 'textures' and sync_type != 'rig':
            sys.solstice.logger.error('Synchronization type {0} is not valid!'.format(sync_type))
            return

        if ask:
            result = qtutils.show_question(None, 'Synchronize file {0}'.format(self._name), 'Are you sure you want to synchronize this asset? This can take quite a lot of time!')
            if result == QMessageBox.No:
                return

        start_time = time.time()

        paths_to_sync = list()

        if status == 'all' or status == 'working':
            if sync_type == 'all':
                paths_to_sync.append(os.path.join(self._asset_path, '__working__'))
            else:
                paths_to_sync.append(os.path.join(self._asset_path, '__working__', sync_type))

        max_versions = self.get_max_published_versions()
        for f, version_list in max_versions.items():
            if not version_list:
                continue
            version_type = version_list[1]
            if status == 'all' or status == 'published':
                if sync_type != 'all':
                    if sync_type in version_type:
                        paths_to_sync.append(os.path.join(self._asset_path, '{0}'.format(version_list[1])))
                else:
                    paths_to_sync.append(os.path.join(self._asset_path, '{0}'.format(version_list[1])))

        syncdialog.SolsticeSyncFile(files=paths_to_sync).sync()
        elapsed_time = time.time() - start_time
        sys.solstice.logger.debug('{0} synchronized in {1} seconds'.format(self._name, elapsed_time))
        self.syncFinished.emit()

    def export_alembic_file(self, file_type='model', start_frame=1, end_frame=1):

        from solstice.pipeline.tools.sanitycheck.checks import assetchecks

        export_path = os.path.dirname(self.get_asset_file(file_type='model', status='working'))
        self.open_asset_file(file_type=file_type, status='working')
        sys.solstice.dcc.refresh_viewport()
        if file_type == 'model':
            object_to_export = '{}_MODEL'.format(self.name)
            if not sys.solstice.dcc.object_exists(object_to_export):
                sys.solstice.logger.error('Model Group {} does not exists!'.format(object_to_export))
                return
            sys.solstice.dcc.rename_node(object_to_export, self.name)

        check = assetchecks.UpdateTag(asset=weakref.ref(self), log=None)
        check.check()

        alembicmanager.AlembicExporter().export_alembic(
            export_path=export_path,
            object_to_export=self.name,
            start_frame=start_frame,
            end_frame=end_frame
        )
        sys.solstice.dcc.new_file()

    def export_standin_file(self, start_frame=1, end_frame=1):
        sys.solstice.dcc.new_file()
        export_path = os.path.dirname(self.get_asset_file(file_type='model', status='working'))
        alembic_name = self.name + '.abc'
        abc_path = os.path.join(export_path, alembic_name)
        if not os.path.isfile(abc_path):
            sys.solstice.logger.warning('Impossible to export Standin file because asset {} has not a valid Alembic file exported: {}'.format(self.name, abc_path))
            return

        alembicmanager.AlembicImporter.reference_alembic(abc_path)
        sys.solstice.dcc.refresh_viewport()
        shaderlibrary.ShaderLibrary.load_all_scene_shaders()
        sys.solstice.dcc.refresh_viewport()
        standinmanager.StandinExporter().export_standin(
            export_path=export_path,
            standin_name=self.name,
            start_frame=start_frame,
            end_frame=end_frame
        )

        sys.solstice.dcc.new_file()

    def import_model_file(self, status='published'):
        asset_name = self._name + '.ma'

        if status == 'published':
            local_max_versions = self.get_max_local_versions()
            if local_max_versions['model']:
                published_path = os.path.join(self._asset_path, local_max_versions['model'][1], 'model', asset_name)
                if os.path.isfile(published_path):
                    artella.import_file_in_maya(file_path=published_path)
        else:
            working_path = os.path.join(self._asset_path, '__working__', 'model')
            if os.path.exists(working_path):
                model_path = os.path.join(working_path, asset_name)
                artella.import_file_in_maya(file_path=model_path)

    def import_proxy_file(self):
        asset_name = self._name+'_PROXY.ma'
        working_path = os.path.join(self._asset_path, '__working__', 'model')
        if os.path.exists(working_path):
            proxy_path = os.path.join(working_path, asset_name)
            artella.import_file_in_maya(file_path=proxy_path)

    def open_textures_folder(self, status):
        if status != 'working' and status != 'published':
            return
        if status == 'working':
            working_path = os.path.join(self._asset_path, '__working__', 'textures')
            if os.path.exists(working_path):
                pythonutils.open_folder(working_path)
        elif status == 'published':
            local_max_versions = self.get_max_local_versions()
            if local_max_versions['textures']:
                published_path = os.path.join(self._asset_path, local_max_versions['textures'][1], 'textures')
                if os.path.exists(published_path):
                    pythonutils.open_folder(published_path)

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        self._asset_info = AssetInfo(asset=self, check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._check_btn = QPushButton('Check')
        for btn in [self._folder_btn, self._artella_btn, self._check_btn]:
            self._asset_info._asset_buttons_layout.addWidget(btn)

        # Create buttons for assets files
        self._working_model_btn = buttons.CategoryButtonWidget(category_name='Model', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_rig_btn = buttons.CategoryButtonWidget(category_name='Rig', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_shading_btn = buttons.CategoryButtonWidget(category_name='Shading', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_textures_btn = buttons.CategoryButtonWidget(category_name='Textures', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_model_btn = buttons.CategoryButtonWidget(category_name='Model', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_rig_btn = buttons.CategoryButtonWidget(category_name='Rig', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_shading_btn = buttons.CategoryButtonWidget(category_name='Shading', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_textures_btn = buttons.CategoryButtonWidget(category_name='Textures', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)

        for btn in [self._working_model_btn, self._working_rig_btn, self._working_shading_btn, self._working_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._working_asset_layout.addWidget(btn)
        for btn in [self._published_model_btn, self._published_rig_btn, self._published_shading_btn, self._published_textures_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._asset_info._published_asset_layout.addWidget(btn)

        self.update_asset_info()

        self._folder_btn.clicked.connect(partial(artella.explore_file, self._asset_path))
        self._artella_btn.clicked.connect(self.open_asset_artella_url)
        self._check_btn.clicked.connect(self.syncFinished.emit)

    def get_asset_artella_url(self):
        file_path = os.path.relpath(self._asset_path, sp.get_solstice_assets_path())
        asset_url = 'https://www.artella.com/project/{0}/files/Assets/{1}'.format(sp.solstice_project_id_raw, file_path)

        return asset_url

    def open_asset_artella_url(self):
        asset_url = self.get_asset_artella_url()
        webbrowser.open(asset_url)

    def get_artella_render_image(self):
        asset_path = self.asset_path
        if asset_path is None or not os.path.exists(asset_path):
            raise RuntimeError('Asset Path {} does not exists!'.format(asset_path))

        asset_data_file = os.path.join(asset_path, '__working__', 'art', self.name+'_render.png')
        if not os.path.isfile(asset_data_file):
            sys.solstice.logger.warning('Asset {} has not a render file available!'.format(self.name))
            return None

        return asset_data_file

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

    def import_builder_file(self):
        asset_name = self._name + '_BUILDER.ma'
        working_path = os.path.join(self._asset_path, '__working__', 'rig')
        if os.path.exists(working_path):
            builder_path = os.path.join(working_path, 'builder')
            if not os.path.isdir(builder_path):
                sys.solstice.logger.warning('Builder Folder for Asset {} does not exists!'.format(self.name))
                return
            builder_path = os.path.join(builder_path, asset_name)
            artella.import_file_in_maya(file_path=builder_path)

    def build_rig(self):
        rig_path = os.path.join(self.asset_path, '__working__', 'rig')
        if not os.path.isdir(rig_path):
            sys.solstice.logger.warning('Asset has no valid rig setup available!'.format(self.name))
            return

        scripts_path = os.path.join(rig_path, 'scripts')
        if not os.path.isdir(scripts_path):
            sys.solstice.logger.warning('Asset has no vlaid rig scripts folder available!'.format(self.name))
            return

        build_script = os.path.join(scripts_path, '{}.py'.format(self.name))
        if not os.path.isfile(build_script):
            sys.solstice.logger.warning('Building Script for Asset {} is not available!'.format(self.name))
            return

        if scripts_path not in sys.path:
            sys.path.append(scripts_path)

        rig_mod = importlib.import_module(self.name)
        if not rig_mod:
            sys.solstice.logger.error('Impossible to import Rig Python Module for {}'.format(self.name))

        if not hasattr(rig_mod, 'build'):
            sys.solstice.logger.warning('Rig Module {} does not implements build function!'.format(rig_mod))
            return

        reload(rig_mod)
        rig_mod.build()

    def has_model(self):
        return True

    def has_shading(self):
        return True

    def has_textures(self):
        return True

    def has_rig(self):
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
        if category == 'rig':
            return self.has_rig()


class CharacterAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(CharacterAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self, check_published_info=False, check_working_info=False, check_lock_info=False):
        super(CharacterAsset, self).generate_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
        if not self._asset_info:
            return

        self._working_groom_btn = buttons.CategoryButtonWidget(category_name='Groom', status='working', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._working_groom_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._asset_info._working_asset_layout.addWidget(self._working_groom_btn)

        self._published_groom_btn = buttons.CategoryButtonWidget(category_name='Groom', status='published', asset=self, check_lock_info=self._asset_info._check_lock_info)
        self._published_groom_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._asset_info._published_asset_layout.addWidget(self._published_groom_btn)

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
        self._has_rig = asset.has_rig()
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
