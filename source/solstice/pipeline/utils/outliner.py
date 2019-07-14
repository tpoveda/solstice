#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains generic widgets to create outliner widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys
from functools import partial
from collections import defaultdict

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.resources import resource

if sp.is_maya():
    import maya.cmds as cmds


class OutlinerItemWidget(QWidget, object):
    clicked = Signal(QObject, QEvent)
    doubleClicked = Signal()
    contextRequested = Signal(QObject, QAction)

    def __init__(self, name, parent=None):
        super(OutlinerItemWidget, self).__init__(parent)

        self.parent = parent
        self.long_name = name
        self.name = name.split('|')[-1]
        self.block_callbacks = False
        self.is_selected = False

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.item_widget = QFrame()
        self.item_layout = QGridLayout()
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_widget.setLayout(self.item_layout)
        self.main_layout.addWidget(self.item_widget)

    def setup_signals(self):
        pass


class OutlinerTreeItemWidget(OutlinerItemWidget, object):
    def __init__(self, name, parent=None):
        self.parent_elem = None
        self.child_elem = dict()
        super(OutlinerTreeItemWidget, self).__init__(name=name, parent=parent)

    def custom_ui(self):
        super(OutlinerTreeItemWidget, self).custom_ui()

        self.child_widget = QWidget()
        self.child_layout = QVBoxLayout()
        self.child_layout.setContentsMargins(0, 0, 0, 0)
        self.child_layout.setSpacing(0)
        self.child_widget.setLayout(self.child_layout)
        self.main_layout.addWidget(self.child_widget)

    def add_child(self, widget, category):
        widget.parent_elem = self
        self.child_elem[category] = widget
        self.child_layout.addWidget(widget)


class OutlinerAssetItem(OutlinerTreeItemWidget, object):
    clicked = Signal(QObject, QEvent)

    def __init__(self, asset, parent=None):
        self.asset = asset
        self.parent = parent
        self.expand_enable = True
        super(OutlinerAssetItem, self).__init__(asset.get_short_name(), parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_selected:
                self.deselect()
            else:
                self.select()
            self.clicked.emit(self, event)

    def contextMenuEvent(self, event):
        if not self.is_selected:
            self.select()

        menu = QMenu(self)
        menu.setStyleSheet('background-color: rgb(68,68,68);')
        menu = self.create_menu(menu)
        action = menu.exec_(self.mapToGlobal(event.pos()))
        self.contextRequested.emit(self, action)

    def custom_ui(self):
        super(OutlinerAssetItem, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

        icon = QIcon()
        icon.addPixmap(QPixmap(':/nudgeDown.png'), QIcon.Normal, QIcon.On)
        icon.addPixmap(QPixmap(':/nudgeRight.png'), QIcon.Normal, QIcon.Off);
        self.expand_btn = QPushButton()
        self.expand_btn.setStyleSheet("QPushButton#expand_btn:checked {background-color: green; border: none}")
        self.expand_btn.setStyleSheet("QPushButton { color:white; } QPushButton:checked { background-color: rgb(55,55, 55); border: none; } QPushButton:pressed { background-color: rgb(55,55, 55); border: none; }")  # \
        self.expand_btn.setFlat(True)
        self.expand_btn.setIcon(icon)
        self.expand_btn.setCheckable(True)
        self.expand_btn.setChecked(True)
        self.expand_btn.setFixedWidth(25)
        self.expand_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.item_layout.addWidget(self.expand_btn, 0, 0, 1, 1)

        self.asset_buttons = self.get_display_widget()
        if self.asset_buttons:
            self.item_layout.addWidget(self.asset_buttons, 0, 1, 1, 1)
        else:
            self.expand_btn.setVisible(False)

        pixmap = self.get_pixmap()
        self.icon_lbl = QLabel()
        self.icon_lbl.setMaximumWidth(18)
        self.icon_lbl.setPixmap(pixmap)
        self.asset_lbl = QLabel(self.name)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

        if self.asset_buttons:
            self.item_layout.addWidget(self.icon_lbl, 0, 2, 1, 1)
            self.item_layout.addWidget(self.asset_lbl, 0, 3, 1, 1)
            self.expand_enable = True
        else:
            self.item_layout.addWidget(self.icon_lbl, 0, 1, 1, 1)
            self.item_layout.addWidget(self.asset_lbl, 0, 2, 1, 1)
            self.expand_enable = False

        self.collapse()

    def setup_signals(self):
        self.expand_btn.clicked.connect(self._on_toggle_children)
        if self.asset_buttons:
            self.asset_buttons.view_btn.toggled.connect(partial(self.viewToggled.emit, self))

    def get_display_widget(self):
        return None

    def get_pixmap(self):
        return QPixmap(':/pickGeometryObj.png')

    def create_menu(self, menu):
        return menu

    def get_file_widget(self, category):
        return self.child_elem.get(category)

    def expand(self):
        self.expand_btn.setChecked(True)
        self._on_toggle_children()

    def collapse(self):
        self.expand_btn.setChecked(False)
        self._on_toggle_children()

    def select(self):
        pass
        # self.is_selected = True
        # self.item_widget.setStyleSheet('QFrame { background-color: rgb(21,60,97);}')

    def deselect(self):
        self.is_selected = False
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

    def set_select(self, select=False):
        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected

    def _on_toggle_children(self):
        state = self.expand_btn.isChecked()
        self.child_widget.setVisible(state)


class OutlinerFileItem(OutlinerTreeItemWidget, object):
    def __init__(self, category, parent=None):
        super(OutlinerFileItem, self).__init__(name=category, parent=parent)

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    @staticmethod
    def get_category_pixmap():
        return QPixmap(':/out_particle.png')

    def custom_ui(self):
        super(OutlinerFileItem, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.setStyleSheet('background-color: rgb(68,68,68);')

        pixmap = self.get_category_pixmap()
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_layout.addWidget(icon_lbl, 0, 1, 1, 1)

        self.target_lbl = QLabel(self.name.title())
        self.item_layout.addWidget(self.target_lbl, 0, 2, 1, 1)


class BaseOutliner(QWidget, object):
    def __init__(self, parent=None):
        super(BaseOutliner, self).__init__(parent=parent)

        self.widget_tree = defaultdict(list)
        self.callbacks = list()
        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    @staticmethod
    def get_file_widget_by_category(category, parent=None):
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            sys.solstice.dcc.clear_selection()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.top_layout = QGridLayout()
        self.top_layout.setAlignment(Qt.AlignLeft)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(2)
        self.main_layout.addLayout(self.top_layout)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(resource.icon('refresh'))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.expand_all_btn = QPushButton()
        self.expand_all_btn.setIcon(resource.icon('expand'))
        self.expand_all_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.collapse_all_btn = QPushButton()
        self.collapse_all_btn.setIcon(resource.icon('collapse'))
        self.collapse_all_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        self.top_layout.addWidget(self.refresh_btn, 0, 0, 1, 1)
        self.top_layout.addWidget(self.expand_all_btn, 0, 1, 1, 1)
        self.top_layout.addWidget(self.collapse_all_btn, 0, 2, 1, 1)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.outliner_layout = QVBoxLayout()
        self.outliner_layout.setContentsMargins(1, 1, 1, 1)
        self.outliner_layout.setSpacing(0)
        self.outliner_layout.addStretch()
        scroll_widget.setLayout(self.outliner_layout)
        self.main_layout.addWidget(scroll_area)

    def setup_signals(self):
        self.refresh_btn.clicked.connect(self._on_refresh_outliner)
        self.expand_all_btn.clicked.connect(self._on_expand_all_assets)
        self.collapse_all_btn.clicked.connect(self._on_collapse_all_assets)

    def init_ui(self):
        pass

    def allowed_types(self):
        return None

    def add_callbacks(self):
        pass

    def remove_callbacks(self):
        for c in self.callbacks:
            try:
                self.callbacks.remove(c)
                del c
            except Exception as e:
                sys.solstice.logger.error('Impossible to clean callback {}'.format(c))
                sys.solstice.logger.error(str(e))

        self.callbacks = list()
        self.scrip_jobs = list()

    def append_widget(self, asset):
        self.widgets.append(asset)
        self.outliner_layout.insertWidget(0, asset)

    def remove_widget(self, asset):
        pass

    def clear_outliner_layout(self):
        del self.widgets[:]
        while self.outliner_layout.count():
            child = self.outliner_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.outliner_layout.setSpacing(0)
        self.outliner_layout.addStretch()

    def refresh_outliner(self):
        self._on_refresh_outliner()

    def _on_refresh_outliner(self, *args):
        self.widget_tree = defaultdict(list)
        self.clear_outliner_layout()
        self.init_ui()
        can_expand = False
        for w in self.widgets:
            if w.expand_enable:
                can_expand = True
        if not can_expand:
            self.expand_all_btn.setVisible(False)
            self.collapse_all_btn.setVisible(False)


    def _on_expand_all_assets(self):
        for asset_widget in self.widget_tree.keys():
            asset_widget.expand()

    def _on_collapse_all_assets(self):
        for asset_widget in self.widget_tree.keys():
            asset_widget.collapse()

    def _on_item_clicked(self, widget, event):
        if widget is None:
            sys.solstice.logger.warning('Selected Asset is not valid!')
            return

        asset_name = widget.asset.name
        item_state = widget.is_selected
        if sys.solstice.dcc.object_exists(asset_name):
            is_modified = event.modifiers() == Qt.ControlModifier
            if not is_modified:
                sys.solstice.dcc.clear_selection()

            for asset_widget, file_items in self.widget_tree.items():
                if asset_widget != widget:
                    continue
                if is_modified and widget.is_selected:
                    cmds.select(asset_widget.asset.name, add=True)
                else:
                    asset_widget.deselect()
                    cmds.select(asset_widget.asset.name, deselect=True)

            widget.set_select(item_state)
            if not is_modified:
                cmds.select(asset_name)
        else:
            self._on_refresh_outliner()

    def _on_selection_changed(self, *args):
        selection = cmds.ls(sl=True, l=True)
        for asset_widget, file_items in self.widget_tree.items():
            if '|{}'.format(asset_widget.asset.name) in selection:
                asset_widget.select()
            else:
                asset_widget.deselect()


class DisplayButtonsWidget(QWidget, object):
    def __init__(self, parent=None):
        super(DisplayButtonsWidget, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.setMouseTracking(True)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        pass

    def setup_signals(self):
        pass


class AssetDisplayButtons(DisplayButtonsWidget, object):

    def __init__(self, parent=None):
        super(AssetDisplayButtons, self).__init__(parent=parent)

    def custom_ui(self):

        self.setMinimumWidth(25)

        self.view_btn = QPushButton()
        self.view_btn.setIcon(QIcon(QPixmap(':/eye.png')))
        self.view_btn.setFlat(True)
        self.view_btn.setFixedWidth(25)
        self.view_btn.setCheckable(True)
        self.view_btn.setChecked(True)
        self.view_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.view_btn)
