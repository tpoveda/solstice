#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_asset.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from solstice_utils import solstice_image as img


class AssetWidget(QWidget, object):

    def __init__(self, name='New_Asset', path=None, category=None, icon=None, icon_format=None, preview=None, preview_format=None, description='', simple_mode=False, checkable=False, parent=None):
        super(AssetWidget, self).__init__(parent=parent)

        self._name = name
        self._asset_path = path
        self._category = category
        self._description = description
        self._icon_format = icon_format
        self._preview_format = preview_format
        self._simple_mode = simple_mode
        self._checkable = checkable
        if icon == '' or icon is None:
            self._icon = None
        else:
            self._icon = icon.encode('utf-8')
        if preview == '' or preview is None:
            self._preview = None
        else:
            self._preview = preview.encode('utf-8')

        self.setMaximumWidth(160)
        self.setMaximumHeight(200)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)
        self.setLayout(main_layout)

        self._asset_btn = QPushButton('', self)
        if self._icon:
            self._asset_btn.setIcon(QPixmap.fromImage(img.base64_to_image(self._icon, image_format=icon_format)))
            self._asset_btn.setIconSize(QSize(150, 150))
        self._asset_label = QLabel(self._name)
        self._asset_label.setAlignment(Qt.AlignCenter)
        asset_menu_layout = QHBoxLayout()
        asset_menu_layout.setContentsMargins(2, 2, 2, 2)
        asset_menu_layout.setSpacing(2)
        self._asset_menu_widget = QWidget()
        self._asset_menu_widget.setLayout(asset_menu_layout)
        for widget in [self._asset_btn, self._asset_menu_widget, self._asset_label]:
            main_layout.addWidget(widget)

        self._asset_btn.setCheckable(self._checkable)

        instance_btn = QPushButton('I')
        asset_menu_layout.addWidget(instance_btn)

        if not self._simple_mode:
            self._asset_btn.clicked.connect(self.toggle_asset_menu)

        self._asset_menu_widget.setVisible(False)

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

    def toggle_asset_menu(self):
        if self._simple_mode:
            return
        self._asset_menu_widget.setVisible(not self._asset_menu_widget.isVisible())

    def contextMenuEvent(self, event):
        menu = self._generate_context_menu()
        menu.exec_(event.globalPos())

    def _generate_context_menu(self):
        """
        This class generates a context menu for the Asset widget depending of the asset
        widget properties
        :return: QMenu
        """

        menu = QMenu(self)
        menu.addAction('Open Asset in Light Rig')
        return menu