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
import threading

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice_pipeline as sp
from solstice_utils import solstice_image as img
from solstice_utils import solstice_artella_utils as artella
from solstice_utils import solstice_artella_classes, solstice_qt_utils
from solstice_gui import solstice_splitters, solstice_published_info_widget, solstice_sync_dialog
from resources import solstice_resource

reload(img)
reload(artella)
reload(solstice_artella_classes)
reload(solstice_qt_utils)
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

    def __init__(self, asset):
        super(AssetInfo, self).__init__()

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
        self._asset_published_info = solstice_published_info_widget.PublishedInfoWidget(asset=asset)
        self._asset_description = QTextEdit()
        self._asset_description.setReadOnly(True)
        self._publish_btn = QPushButton('> PUBLISH NEW VERSION <')
        main_layout.addWidget(self._asset_info_lbl)
        main_layout.addWidget(self._asset_icon)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addLayout(self._buttons_layout)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addWidget(solstice_splitters.Splitter('PUBLISHED INFO'))
        main_layout.addWidget(self._asset_published_info)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        main_layout.addWidget(self._asset_description)
        main_layout.addWidget(self._publish_btn)

class AssetWidget(QWidget, object):

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
        self._menu.addAction(sync_action)

        check_versions_action = QAction('Check for New Versions', self._menu)
        self._menu.addAction(check_versions_action)

        get_info_action.triggered.connect(self.get_asset_info)
        sync_action.triggered.connect(self.sync)

    def get_asset_info(self):
        # rsp = artella.get_status(os.path.join(self._asset_path, '__model_v001__'), as_json=True)
        rsp = artella.get_status(self._asset_path, as_json=True)
        print(rsp)

    def sync(self):
        result = solstice_qt_utils.show_question(None, 'Synchronize file {0}'.format(self._name), 'Are you sure you want to synchronize this asset? This can take quite a lot of time!')
        if result == QMessageBox.Yes:
            solstice_sync_dialog.SolsticeSyncFile(files=[self._asset_path]).sync()

    def generate_asset_info_widget(self):
        self._asset_info = AssetInfo(asset=self)
        self.update_asset_info()

    def get_asset_info_widget(self):
        self.generate_asset_info_widget()
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

    def generate_asset_info_widget(self):
        super(CharacterAsset, self).generate_asset_info_widget()
        if not self._asset_info:
            return

        self._model_btn = QPushButton('Model')
        self._shading_btn = QPushButton('Shading')
        self._textures_btn = QPushButton('Textures')
        self._groom_btn = QPushButton('Groom')
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._sync_btn = QPushButton('Sync')
        for btn in [self._model_btn, self._shading_btn, self._textures_btn, self._groom_btn, self._folder_btn, self._artella_btn, self._sync_btn]:
            self._asset_info._buttons_layout.addWidget(btn)

    def update_asset_info(self):
        super(CharacterAsset, self).update_asset_info()


class PropAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(PropAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self):
        super(PropAsset, self).generate_asset_info_widget()

        self._model_btn = QPushButton('Model')
        self._shading_btn = QPushButton('Shading')
        self._textures_btn = QPushButton('Textures')
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._sync_btn = QPushButton('Sync')
        for btn in [self._model_btn, self._shading_btn, self._textures_btn, self._folder_btn, self._artella_btn, self._sync_btn]:
            self._asset_info._buttons_layout.addWidget(btn)

    def update_asset_info(self):
        super(PropAsset, self).update_asset_info()


class BackgroundElementAsset(AssetWidget, object):
    def __init__(self, **kwargs):
        super(BackgroundElementAsset, self).__init__(**kwargs)

    def generate_asset_info_widget(self):
        super(BackgroundElementAsset, self).generate_asset_info_widget()

        self._model_btn = QPushButton('Model')
        self._shading_btn = QPushButton('Shading')
        self._textures_btn = QPushButton('Textures')
        self._folder_btn = QPushButton('Folder')
        self._artella_btn = QPushButton('Artella')
        self._sync_btn = QPushButton('Sync')
        for btn in [self._model_btn, self._shading_btn, self._textures_btn, self._folder_btn, self._artella_btn, self._sync_btn]:
            self._asset_info._buttons_layout.addWidget(btn)

    def update_asset_info(self):
        super(BackgroundElementAsset, self).update_asset_info()
