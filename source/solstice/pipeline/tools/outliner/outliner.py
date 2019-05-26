#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ool used to show assets related with Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys
import weakref
import collections
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import solstice.pipeline as sp
from solstice.pipeline.core import node
from solstice.pipeline.gui import messagehandler, stack
from solstice.pipeline.utils import mayautils, qtutils
from solstice.pipeline.resources import resource


global solstice_outliner_window
try:
    # We do this to remove callbacks when we reload the module
    # Only during DEV
    solstice_outliner_window.remove_callbacks()
except Exception:
    pass


class OutlinerTreeItemWidget(QWidget, object):
    clicked = Signal(QObject)
    viewToggled = Signal(QObject)
    nameChanged = Signal(QObject)

    def __init__(self, name, parent=None):
        super(OutlinerTreeItemWidget, self).__init__(parent)

        self.setMouseTracking(True)

        self.parent = parent
        self.long_name = name
        self.name = name.split('|')[-1]
        self.block_callbacks = False
        self.is_selected = False
        self.parent_elem = None
        self.child_elem = dict()

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

    def add_child(self, widget, category):
        widget.parent_elem = self
        self.child_elem[category] = widget
        self.child_layout.addWidget(widget)


class OutlinerAssetItem(OutlinerTreeItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)
    viewToggled = Signal(QObject, bool)
    viewSolo = Signal(QObject, bool)

    def __init__(self, asset, parent=None):

        self.asset = asset
        self.parent = parent

        super(OutlinerAssetItem, self).__init__(asset.get_short_name(), parent)

        self.collapse()

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
        self.asset_buttons.view_btn.toggled.connect(partial(self.viewToggled.emit, self))

    def add_asset_attributes_change_callback(self):
        obj = self.asset.get_mobject()
        vis_callback = OpenMaya.MNodeMessage.addAttributeChangedCallback(obj, partial(self._update_asset_attributes))
        return vis_callback

    def _update_asset_attributes(self, msg, plug, otherplug, *client_data):

        if self.block_callbacks is False:
            if msg & OpenMaya.MNodeMessage.kAttributeSet:
                if 'visibility' in plug.name():
                    self.asset_buttons.view_btn.setChecked(plug.asBool())
                elif 'type' in plug.name():
                    model_widget = self.get_file_widget(category='model')
                    if model_widget is None:
                        sys.solstice.logger.warning('Impossible to update type attribute because model wigdet is available!')
                        return
                    model_widget.model_buttons.proxy_hires_cbx.setCurrentIndex(plug.asInt())

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
        replace_menu = QMenu('Replace by', self)
        menu.addMenu(replace_menu)
        replace_abc = replace_menu.addAction('Alembic')
        replace_rig = replace_menu.addAction('Rig')
        replace_standin = replace_menu.addAction('Standin')
        remove_act = menu.addAction('Delete')
        menu.addSeparator()
        sync_shaders_act = menu.addAction('Sync Shaders')
        unload_shaders_act = menu.addAction('Unload Shaders')

        replace_abc.triggered.connect(self._on_replace_alembic)
        replace_rig.triggered.connect(self._on_replace_rig)
        sync_shaders_act.triggered.connect(self._on_sync_shaders)
        unload_shaders_act.triggered.connect(self._on_unload_shaders)

        action = menu.exec_(self.mapToGlobal(event.pos()))
        self.contextRequested.emit(self, action)

    def get_file_widget(self, category):
        return self.child_elem.get(category)

    def select(self):
        pass
        # self.is_selected = True
        # self.item_widget.setStyleSheet('QFrame { background-color: rgb(21,60,97);}')

    def deselect(self):
        self.is_selected = False
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

    def expand(self):
        self.expand_btn.setChecked(True)
        self._on_toggle_children()

    def collapse(self):
        self.expand_btn.setChecked(False)
        self._on_toggle_children()

    def set_select(self, select=False):
        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected

    def is_rig(self):
        """
        Returns whether current asset is a rig or not
        :return: bool
        """

        valid_tag_data = False
        main_group_connections = cmds.listConnections(self.asset.node, source=True)
        for connection in main_group_connections:
            attrs = cmds.listAttr(connection, userDefined=True)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        print(valid_tag_data)

    def is_alembic(self):
        """
        Returns whether current asset is an alembic or not
        :return: bool
        """

        valid_tag_data = False
        main_group_connections = cmds.listConnections(self.asset.node, source=True)
        for connection in main_group_connections:
            attrs = cmds.listAttr(connection, userDefined=True)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        print(valid_tag_data)

    def is_standin(self):
        """
        Returns whether current asset is an standin or not
        :return: bool
        """

        pass

    def _on_toggle_children(self):
        state = self.expand_btn.isChecked()
        self.child_widget.setVisible(state)

    def _on_replace_alembic(self):
        abc_file = self.asset.get_alembic_files()
        is_referenced = sys.solstice.dcc.node_is_referenced(self.asset.node)
        self.is_rig()
        # if self.asset.node != hires_group:
        #     is_referenced = cmds.referenceQuery(asset.node, isNodeReferenced=True)
        #     if is_referenced:
        #         namespace = cmds.referenceQuery(asset.node, namespace=True)
        #         if not namespace or not namespace.startswith(':'):
        #             sys.solstice.logger.error('Node {} has not a valid namespace!. Please contact TD!'.format(asset.node))
        #             continue
        #         else:
        #             namespace = namespace[1:] + ':'

    def _on_replace_rig(self):
        is_referenced = sys.solstice.dcc.node_is_referenced(self.asset.node)
        if not is_referenced:
            valid_refs = True
            children = sys.solstice.dcc.node_children(self.asset.node, all_hierarchy=False, full_path=True)
            for child in children:
                is_child_ref = sys.solstice.dcc.node_is_referenced(child)
                if not is_child_ref:
                    valid_refs = False
                    break
            if not valid_refs:
                sys.solstice.logger.warning('Impossible to replace {} by rig file ...'.format(self.asset.node))
                return
            rig_ref = self.asset.reference_asset_file('rig')
            print(rig_ref)

    def _on_sync_shaders(self):
        self.asset.sync_shaders()

    def _on_unload_shaders(self):
        self.asset.unload_shaders()


class OutlinerFileItem(OutlinerTreeItemWidget, object):
    clicked = Signal(QObject, QEvent)
    doubleClicked = Signal()
    contextRequested = Signal(QObject, QAction)

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


class OutlinerModelItem(OutlinerFileItem, object):

    proxyHiresToggled = Signal(QObject, int)

    def __init__(self, parent=None):
        super(OutlinerModelItem, self).__init__(category='model', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return resource.pixmap('cube', category='icons').scaled(18, 18, Qt.KeepAspectRatio)

    def custom_ui(self):
        super(OutlinerModelItem, self).custom_ui()

        self.model_buttons = ModelDisplayButtons()
        self.item_layout.addWidget(self.model_buttons, 0, 3, 1, 1)

    # def setup_signals(self):
    #     self.model_buttons.proxy_hires_cbx.currentIndexChanged.connect(partial(self.proxyHiresToggled.emit, self))


class OutlinerShadingItem(OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerShadingItem, self).__init__(category='shading', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return  resource.pixmap('shader', category='icons').scaled(18, 18, Qt.KeepAspectRatio)


class OutlinerGroomItem(OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerGroomItem, self).__init__(category='groom', parent=parent)


class OutlinerArtellaItem(OutlinerFileItem, object):
    def __init__(self, parent=None):
        super(OutlinerArtellaItem, self).__init__(category='artella', parent=parent)

    @staticmethod
    def get_category_pixmap():
        return resource.pixmap('artella', category='icons').scaled(18, 18, Qt.KeepAspectRatio)


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


class ModelDisplayButtons(DisplayButtonsWidget, object):
    def __init__(self, parent=None):
        super(ModelDisplayButtons, self).__init__(parent=parent)

    def custom_ui(self):
        self.setMinimumWidth(25)

        self.proxy_hires_cbx = QComboBox()
        self.proxy_hires_cbx.addItem('proxy')
        self.proxy_hires_cbx.addItem('hires')
        self.proxy_hires_cbx.addItem('both')
        self.main_layout.addWidget(self.proxy_hires_cbx)


class ArtellaDisplayButtons(DisplayButtonsWidget, object):
    def __init__(self, parent=None):
        super(ArtellaDisplayButtons, self).__init__(parent=parent)

    def custom_ui(self):
        self.setMinimumWidth(25)


class SolsticeAbstractOutliner(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeAbstractOutliner, self).__init__(parent=parent)

        self.widget_tree = collections.defaultdict(list)
        self.callbacks = list()
        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    @staticmethod
    def get_file_widget_by_category(category, parent=None):
        if category == 'model':
            file_widget = OutlinerModelItem(parent=parent)
        elif category == 'shading':
            file_widget = OutlinerShadingItem(parent=parent)
        elif category == 'groom':
            file_widget = OutlinerGroomItem(parent=parent)
        elif category == 'artella':
            file_widget = OutlinerArtellaItem(parent=parent)
        else:
            return None

        return file_widget

    @staticmethod
    def get_assets(allowed_types='all'):

        asset_nodes = list()

        if not allowed_types:
            return asset_nodes

        # We find tag data nodes
        tag_data_nodes = SolsticeOutliner.get_tag_data_nodes()
        for tag_data in tag_data_nodes:
            asset = tag_data.get_asset()
            if asset is None:
                continue
            if allowed_types and allowed_types != 'all':
                asset_type = tag_data.get_types()
                if asset_type not in allowed_types:
                    continue
                asset_nodes.append(asset)
            else:
                asset_nodes.append(asset)

        # We find nodes with tag info attribute (alembics)
        tag_info_nodes = SolsticeOutliner.get_tag_info_nodes()
        for tag_data in tag_info_nodes:
            asset = tag_data.get_asset()
            if asset is None:
                continue
            if allowed_types and allowed_types != 'all':
                asset_type = tag_data.get_types()
                if asset_type not in allowed_types:
                    continue
                asset_nodes.append(asset)
            else:
                asset_nodes.append(asset)

        return asset_nodes

    def custom_ui(self):
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(resource.icon('refresh'))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.refresh_btn, 0, 0, 1, 1)

        self.expand_all_btn = QPushButton()
        self.expand_all_btn.setIcon(resource.icon('expand'))
        self.expand_all_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.expand_all_btn, 0, 1, 1, 1)

        self.collapse_all_btn = QPushButton()
        self.collapse_all_btn.setIcon(resource.icon('collapse'))
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
        allowed_types = self.allowed_types()
        assets = self.get_assets(allowed_types=allowed_types)
        for asset in assets:
            asset_widget = OutlinerAssetItem(asset)
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()

            asset_widget.clicked.connect(self._on_item_clicked)
            asset_widget.viewToggled.connect(self._on_toggle_view)
            self.callbacks.append(mayautils.MCallbackIdWrapper(asset_widget.add_asset_attributes_change_callback()))

            asset_files = asset.get_asset_files()
            asset_files['artella'] = None
            for cat, file_path in asset_files.items():
                file_widget = self.get_file_widget_by_category(category=cat, parent=asset_widget)
                if file_widget is not None:
                    asset_widget.add_child(file_widget, category=cat)
                    self.widget_tree[asset_widget].append(file_widget)
                    if cat == 'model':
                        file_widget.proxyHiresToggled.connect(self._on_toggle_proxy_hires)
                    elif cat == 'shading':
                        pass
                    elif cat == 'groom':
                        pass
                    elif cat == 'artella':
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

    def _on_item_clicked(self, widget, event):
        if widget is None:
            sys.solstice.logger.warning('Selected Asset is not valid!')
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

    def _on_toggle_view(self, widget, state):
        node_name = widget.asset.node
        if cmds.objExists(node_name):
            main_control = widget.asset.get_main_control()
            if main_control:
                if not cmds.objExists(main_control):
                    return
            # if not main_control or not cmds.objExists(main_control):
            #     if state:
            #
            #     return
            if state is True:
                cmds.showHidden(node_name)
            else:
                cmds.hide(node_name)

    def _on_toggle_proxy_hires(self, widget, item_index):
        node_name = widget.parent.asset.node
        if cmds.objExists(node_name):
            if cmds.attributeQuery('type', node=node_name, exists=True):
                widget.parent.block_callbacks = True
                try:
                    cmds.setAttr('{}.type'.format(node_name), item_index)
                except Exception:
                    widget.parent.block_callbacks = False
                widget.parent.block_callbacks = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cmds.select(clear=True)


class SolsticeAssetsOutliner(SolsticeAbstractOutliner, object):

    def __init__(self, parent=None):
        super(SolsticeAssetsOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['prop']

    def add_callbacks(self):
        pass
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('NameChanged', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneOpened', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('SceneImported', self._on_refresh_outliner)))
        # # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Undo', self._on_refresh_outliner)))
        # # self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(OpenMaya.MEventMessage.addEventCallback('Redo', self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, self._on_refresh_outliner)))
        # self.callbacks.append(mayautils.MCallbackIdWrapper(OpenMaya.MDGMessage.addNodeRemovedCallback(self._on_refresh_outliner)))

class SolsticeCharactersOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCharactersOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['character']


class SolsticeLightsOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeLightsOutliner, self).__init__(parent=parent)


class SolsticeCamerasOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCamerasOutliner, self).__init__(parent=parent)


class SolsticeFXOutliner(SolsticeAbstractOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeFXOutliner, self).__init__(parent=parent)


class SolsticeOutlinerSettings(QWidget, object):

    settingsSaved = Signal()

    def __init__(self, parent=None):
        super(SolsticeOutlinerSettings, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.save_btn = QPushButton('Save')
        self.save_btn.setIcon(resource.icon('save'))
        self.main_layout.addWidget(self.save_btn)

    def setup_signals(self):
        self.save_btn.clicked.connect(self.settingsSaved.emit)


class SolsticeTabs(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeTabs, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.assets_outliner = SolsticeAssetsOutliner()
        self.characters_outliner = SolsticeCharactersOutliner()
        self.lights_outliner = SolsticeLightsOutliner()
        self.fx_outliner = SolsticeFXOutliner()
        self.cameras_outliner = SolsticeCamerasOutliner()

        self.tab_widget.addTab(self.assets_outliner, 'Assets')
        self.tab_widget.addTab(self.characters_outliner, 'Characters')
        self.tab_widget.addTab(self.lights_outliner, 'Lights')
        self.tab_widget.addTab(self.fx_outliner, 'FX')
        self.tab_widget.addTab(self.cameras_outliner, 'Cameras')

    def setup_signals(self):
        pass

    def get_count(self):
        return self.tab_widget.count()

    def get_widget(self, index):
        return self.tab_widget.widget(index)


class SolsticeOutliner(QWidget, object):

    name = 'SolsticeOutliner'
    title = 'Solstice Tools - Solstice Outliner'
    version = '1.2'

    instances = list()

    def __init__(self, parent=mayautils.get_maya_window()):
        super(SolsticeOutliner, self).__init__(parent=parent)

        SolsticeOutliner._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        cmds.select(clear=True)

        self.io = messagehandler.MessageHandler()

        self.custom_ui()
        self.init_ui()
        self.setup_signals()

        global solstice_outliner_window
        solstice_outliner_window = self

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

    @staticmethod
    def get_tag_data_nodes():
        tag_nodes = list()
        objs = cmds.ls(l=True)
        for obj in objs:
            valid_tag_data = cmds.attributeQuery('tag_type', node=obj, exists=True)
            if valid_tag_data:
                tag_type = cmds.getAttr(obj + '.tag_type')
                if tag_type and tag_type == 'SOLSTICE_TAG':
                    tag_node = node.SolsticeTagDataNode(node=obj)
                    tag_nodes.append(tag_node)

        return tag_nodes

    @staticmethod
    def get_tag_info_nodes():
        tag_info_nodes = list()
        objs = cmds.ls(l=True)
        for obj in objs:
            valid_tag_info_data = cmds.attributeQuery('tag_info', node=obj, exists=True)
            if valid_tag_info_data:
                tag_info = cmds.getAttr(obj+'.tag_info')
                tag_node = node.SolsticeTagDataNode(node=obj, tag_info=tag_info)
                tag_info_nodes.append(tag_node)

        return tag_info_nodes

    @staticmethod
    def load_shaders():
        if not sp.is_maya():
            return

        from solstice.pipeline.tools.shaderlibrary import shaderlibrary
        reload(shaderlibrary)

        shaderlibrary.ShaderLibrary.load_all_scene_shaders()

    def unload_shaders(self):
        if not sp.is_maya():
            return

        from solstice.pipeline.tools.shaderlibrary import shaderlibrary
        reload(shaderlibrary)

        shaderlibrary.ShaderLibrary.unload_shaders()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.parent().layout().addLayout(self.main_layout)

        self.toolbar = QToolBar()
        self.setup_toolbar()
        self.main_layout.addWidget(self.toolbar)

        self.stack = stack.SlidingStackedWidget(self)
        self.main_layout.addWidget(self.stack)

        self.tabs = SolsticeTabs(self)
        self.settingswidget = SolsticeOutlinerSettings()

        self.stack.addWidget(self.tabs)
        self.stack.addWidget(self.settingswidget)

    def setup_signals(self):
        self.settingswidget.settingsSaved.connect(self.open_tabs)

    def setup_toolbar(self):
        load_scene_shaders_action = QToolButton(self)
        load_scene_shaders_action.setText('Load Shaders')
        load_scene_shaders_action.setToolTip('Load and Apply All Scene Shaders')
        load_scene_shaders_action.setStatusTip('Load and Apply All Scene Shaders')
        load_scene_shaders_action.setIcon(resource.icon('apply_shaders'))
        load_scene_shaders_action.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        unload_scene_shaders_action = QToolButton(self)
        unload_scene_shaders_action.setText('Unload Shaders')
        unload_scene_shaders_action.setToolTip('Unload All Scene Shaders')
        unload_scene_shaders_action.setStatusTip('Unload All Scene Shaders')
        unload_scene_shaders_action.setIcon(resource.icon('unload_shaders'))
        unload_scene_shaders_action.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        settings_action = QToolButton(self)
        settings_action.setText('Settings')
        settings_action.setToolTip('Outliner Settings')
        settings_action.setStatusTip('Outliner Settings')
        settings_action.setIcon(resource.icon('settings'))
        settings_action.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.toolbar.addWidget(load_scene_shaders_action)
        self.toolbar.addWidget(unload_scene_shaders_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(settings_action)

        load_scene_shaders_action.clicked.connect(self.load_shaders)
        unload_scene_shaders_action.clicked.connect(self.unload_shaders)
        settings_action.clicked.connect(self.open_settings)

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

    def open_tabs(self):
        self.stack.slide_in_index(0)

    def open_settings(self):
        self.stack.slide_in_index(1)

    def closeEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def hideEvent(self, event):
        self.remove_callbacks()
        event.accept()

    def deleteLater(self):
        self.remove_callbacks()
        super(SolsticeOutliner, self).deleteLater()

    def get_outliner_widgets(self):
        outliner_widgets = list()
        for i in range(self.tabs.get_count()):
            outliner_widgets.append(self.tabs.get_widget(i))

        return outliner_widgets

    def run(self):
        self.add_callbacks()
        return self


def run():
    qtutils.dock_window(SolsticeOutliner)
