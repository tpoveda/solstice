#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_outliner.py
# by Tomas Poveda
# Tool used to show assets related with Solstice
# ______________________________________________________________________
# ==================================================================="""

import sys
import weakref
import collections

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_node, solstice_maya_utils, solstice_qt_utils
from solstice_pipeline.solstice_gui import solstice_messagehandler
from solstice_pipeline.resources import solstice_resource

global solstice_outliner_window
try:
    # We do this to remove callbacks when we reload the module
    # Only during DEV
    solstice_outliner_window.remove_callbacks()
except:
    pass


class OutlinerTreeItemWidget(QWidget, object):
    clicked = Signal(QObject)
    viewToggled = Signal(QObject)
    nameChanged = Signal(QObject)

    def __init__(self, name, parent=None):
        super(OutlinerTreeItemWidget, self).__init__(parent)

        self.parent = parent
        self.long_name = name
        self.name = name.split('|')[-1]
        self.is_selected = False
        self.parent_elem = None
        self.child_elem = list()

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

        self.child_widget = QWidget()
        self.child_layout = QVBoxLayout()
        self.child_layout.setContentsMargins(0, 0, 0, 0)
        self.child_layout.setSpacing(0)
        self.child_widget.setLayout(self.child_layout)
        self.main_layout.addWidget(self.child_widget)

    def setup_signals(self):
        pass

    def add_child(self, widget):
        widget.parent_elem = self
        self.child_elem.append(widget)
        self.child_layout.addWidget(widget)


class OutlinerAssetItem(OutlinerTreeItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)
    viewToggled = Signal(QObject, int)
    viewSolo = Signal(QObject, bool)

    def __init__(self, asset, parent=None):

        self.asset = asset
        self.parent = parent

        super(OutlinerAssetItem, self).__init__(asset.get_short_name(), parent)

    def custom_ui(self):
        super(OutlinerAssetItem ,self).custom_ui()

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

        self.asset_buttons = AssetDisplayButtons()
        self.item_layout.addWidget(self.asset_buttons, 0, 1, 1, 1)

        pixmap = QPixmap(':/pickGeometryObj.png')
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_layout.addWidget(icon_lbl, 0, 2, 1, 1)

        self.asset_lbl = QLabel(self.name)
        self.item_layout.addWidget(self.asset_lbl, 0, 3, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

    def setup_signals(self):
        self.expand_btn.clicked.connect(self._on_toggle_children)

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
        remove_act = menu.addAction('Delete')
        menu.addSeparator()
        action = menu.exec_(self.mapToGlobal(event.pos()))
        self.contextRequested.emit(self, action)

    def select(self):
        self.is_selected = True
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(21,60,97);}')

    def deselect(self):
        self.is_selected = False
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

    def expand(self):
        self.expand_btn.setChecked(True)
        self._on_toggle_children()

    def collapse(self):
        self.expand_btn.setChecked(False)
        self._on_toggle_children()

    def _on_toggle_children(self):
        state = self.expand_btn.isChecked()
        self.child_widget.setVisible(state)

    def set_select(self, select=False):
        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected


class OutlinerFileItem(OutlinerTreeItemWidget, object):
    clicked = Signal(QObject, QEvent)
    doubleClicked = Signal()
    contextRequested = Signal(QObject, QAction)

    def __init__(self, category, parent=None):
        super(OutlinerFileItem, self).__init__(name=category, parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        super(OutlinerFileItem, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.setStyleSheet('background-color: rgb(68,68,68);')

        pixmap = QPixmap(':/out_particle.png')
        icon_lbl = QLabel()
        icon_lbl.setMaximumWidth(18)
        icon_lbl.setPixmap(pixmap)
        self.item_layout.addWidget(icon_lbl, 0, 1, 1, 1)

        self.target_lbl = QLabel(self.name.title())
        self.item_layout.addWidget(self.target_lbl, 0, 2, 1, 1)

        self.target_edt = QLineEdit(self.item_widget)
        self.target_edt.setStyleSheet("background-color: rgb(68,68,68);")
        self.target_edt.setMinimumWidth(180)
        self.target_edt.setVisible(False)
        self.item_layout.addWidget(self.target_edt, 0, 2, 1, 1)

        self.item_layout.setColumnStretch(2, 1)


class DisplayButtonsWidget(QWidget, object):
    def __init__(self, parent=None):
        super(DisplayButtonsWidget, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

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


class SolsticeAbstractOutliner(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeAbstractOutliner, self).__init__(parent=parent)

        self.widget_tree = collections.defaultdict(list)
        self.callbacks = list()
        self.widgets = list()

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(solstice_resource.icon('refresh'))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.refresh_btn, 0, 0, 1, 1)

        self.expand_all_btn = QPushButton()
        self.expand_all_btn.setIcon(solstice_resource.icon('expand'))
        self.expand_all_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.expand_all_btn, 0, 1, 1, 1)

        self.collapse_all_btn = QPushButton()
        self.collapse_all_btn.setIcon(solstice_resource.icon('collapse'))
        self.collapse_all_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.collapse_all_btn, 0, 2, 1, 1)

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
        self.main_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        self.refresh_btn.clicked.connect(self._on_refresh_outliner)
        self.expand_all_btn.clicked.connect(self._on_expand_all_assets)
        self.collapse_all_btn.clicked.connect(self._on_collapse_all_assets)

    def init_ui(self):
        pass

    def add_callbacks(self):
        pass

    def remove_callbacks(self):
        for c in self.callbacks:
            try:
                self.callbacks.remove(c)
                del c
            except Exception as e:
                sp.logger.error('Impossible to clean callback {}'.format(c))
                sp.logger.error(str(e))
        self.callbacks = list()

    def append_widget(self, asset):
        self.widgets.append(asset)
        self.outliner_layout.insertWidget(0, asset)

    def remove_widget(self, asset):
        pass

    def refresh_outliner(self):
        self._on_refresh_outliner()

    def clear_outliner_layout(self):
        del self.widgets[:]
        while self.outliner_layout.count():
            child = self.outliner_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.outliner_layout.setSpacing(0)
        self.outliner_layout.addStretch()

    def _on_refresh_outliner(self, *args):
        self.widget_tree = collections.defaultdict(list)
        self.clear_outliner_layout()
        self.init_ui()

    def _on_expand_all_assets(self):
        for asset_widget in self.widget_tree.keys():
            asset_widget.expand()

    def _on_collapse_all_assets(self):
        for asset_widget in self.widget_tree.keys():
            asset_widget.collapse()




class SolsticeAssetsOutliner(SolsticeAbstractOutliner, object):

    def __init__(self, parent=None):
        super(SolsticeAssetsOutliner, self).__init__(parent=parent)

    def add_callbacks(self):
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('NameChanged', self._on_refresh_outliner)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneOpened', self._on_refresh_outliner)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneImported', self._on_refresh_outliner)))
        # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Undo', self._on_refresh_outliner)))
        # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Redo', self._on_refresh_outliner)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self._on_refresh_outliner)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self._on_refresh_outliner)))
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MDGMessage.addNodeRemovedCallback(self._on_refresh_outliner)))

    def init_ui(self):
        assets = self.get_assets()
        for asset in assets:
            asset_widget = OutlinerAssetItem(asset)
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()
            asset_widget.clicked.connect(self._on_item_clicked)
            asset_files = asset.get_asset_files()
            for cat, file_path in asset_files.items():
                file_widget = OutlinerFileItem(category=cat, parent=asset_widget)
                asset_widget.add_child(file_widget)
                self.widget_tree[asset_widget].append(file_widget)

    @staticmethod
    def get_assets():
        asset_nodes = list()
        tag_data_nodes = SolsticeOutliner.get_tag_data_nodes()
        for tag_data in tag_data_nodes:
            asset = tag_data.get_asset()
            if asset is None:
                continue
            asset_nodes.append(asset)

        return asset_nodes

    def _on_item_clicked(self, widget, event):
        if widget is None:
            sp.logger.warning('Selected Asset is not valid!')
            return

        asset_name = widget.asset.name
        item_state = widget.is_selected
        if cmds.objExists(asset_name):
            is_modified = event.modifiers() == Qt.ControlModifier
            if not is_modified:
                cmds.select(clear=True)

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


class SolsticeCharactersOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCharactersOutliner, self).__init__(parent=parent)


class SolsticeLightsOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeLightsOutliner, self).__init__(parent=parent)


class SolsticeCamerasOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCamerasOutliner, self).__init__(parent=parent)


class SolsticeFXOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeFXOutliner, self).__init__(parent=parent)


class SolsticeOutliner(QWidget, object):

    name = 'SolsticeOutliner'
    title = 'Solstice Tools - Solstice Outliner'
    version = '1.1'

    instances = list()

    def __init__(self, parent=solstice_maya_utils.get_maya_window()):
        super(SolsticeOutliner, self).__init__(parent=parent)

        SolsticeOutliner._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        cmds.select(clear=True)

        self.io = solstice_messagehandler.MessageHandler()

        self.custom_ui()
        self.init_ui()
        self.setup_signals()

        global solstice_outliner_window
        solstice_outliner_window = self

    @staticmethod
    def get_tag_data_nodes():
        tag_nodes = list()
        objs = cmds.ls(l=True)
        for obj in objs:
            valid_tag_data = cmds.attributeQuery('tag_type', node=obj, exists=True)
            if valid_tag_data:
                tag_type = cmds.getAttr(obj + '.tag_type')
                if tag_type and tag_type == 'SOLSTICE_TAG':
                    tag_node = solstice_node.SolsticeTagDataNode(node=obj)
                    tag_nodes.append(tag_node)

        return tag_nodes

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.parent().layout().addLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.assets_outliner = SolsticeAssetsOutliner()
        self.characters_outliner = SolsticeCharactersOutliner()
        self.lights_outliner = SolsticeLightsOutliner()
        self.fx_outliner = SolsticeFXOutliner()
        self.cameras_outliner = SolsticeCamerasOutliner()
        #
        self.tab_widget.addTab(self.assets_outliner, 'Assets')
        self.tab_widget.addTab(self.characters_outliner, 'Characters')
        self.tab_widget.addTab(self.lights_outliner, 'Lights')
        self.tab_widget.addTab(self.fx_outliner, 'FX')
        self.tab_widget.addTab(self.cameras_outliner, 'Cameras')


    def setup_signals(self):
        pass

    def init_ui(self):
        for outliner in self.get_outliner_widgets():
            outliner.init_ui()

    def add_callbacks(self):
        for outliner in self.get_outliner_widgets():
            outliner.add_callbacks()

    def remove_callbacks(self):
        for outliner in self.get_outliner_widgets():
            outliner.remove_callbacks()

    def refresh_outliner(self):
        for outliner in self.get_outliner_widgets():
            outliner.refresh_outliner()

    def closeEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def hideEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def deleteLater(self):
        self.remove_callbacks()
        super(SolsticeOutliner, self).deleteLater()

    @staticmethod
    def _delete_instances():
        for ins in SolsticeOutliner.instances:
            try:
                ins.remove_callbacks()
                ins.setParent(None)
                ins.deleteLater()
            except Exception:
                pass

            SolsticeOutliner.instances.remove(ins)
            del ins

    def get_outliner_widgets(self):
        outliner_widgets = list()
        for i in range(self.tab_widget.count()):
            outliner_widgets.append(self.tab_widget.widget(i))

        return outliner_widgets

    def run(self):
        self.add_callbacks()
        return self


def run():
    solstice_qt_utils.dock_window(SolsticeOutliner)



