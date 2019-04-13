#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shotassembler.py
# by Tomas Poveda
# Tool to load shot elements
# ______________________________________________________________________
# ==================================================================="""

import os
import json

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters, solstice_attributes
from solstice_pipeline.solstice_utils import solstice_node, solstice_image as img
from solstice_pipeline.resources import solstice_resource

reload(solstice_node)


class AbstractItemWidget(QWidget, object):
    def __init__(self, asset, parent=None):
        super(AbstractItemWidget, self).__init__(parent)

        self.asset = asset
        self.parent = parent

        self.is_selectable = True
        self.setMouseTracking(True)
        self.is_selected = False
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.custom_ui()
        self.setup_signals()

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_selected:
                self.deselect()
            else:
                self.select()
            self.clicked.emit(self, event)

    def select(self):
        if not self.is_selectable:
            return

        self.is_selected = True
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(21,60,97);}')

    def deselect(self):
        if not self.is_selectable:
            return

        self.is_selected = False
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

    def set_select(self, select=False):
        if not self.is_selectable:
            return

        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected


class ShotAsset(AbstractItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, asset, parent=None):
        super(ShotAsset, self).__init__(asset, parent)
        self.is_selectable = False

    def custom_ui(self):
        super(ShotAsset, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

        self.asset_lbl = QLabel(os.path.basename(self.asset))
        self.asset_lbl.setToolTip(self.asset)
        self.item_layout.addWidget(self.asset_lbl, 0, 1, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)


class ShotAssets(QWidget, object):

    updateHierarchy = Signal()

    def __init__(self, parent=None):
        super(ShotAssets, self).__init__(parent=parent)

        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

        self.update_menu()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.add_btn = QPushButton('Add Asset')
        self.main_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.assets_menu = QMenu()
        self.add_btn.setMenu(self.assets_menu)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.assets_layout = QVBoxLayout()
        self.assets_layout.setContentsMargins(1, 1, 1, 1)
        self.assets_layout.setSpacing(0)
        self.assets_layout.addStretch()
        scroll_widget.setLayout(self.assets_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        pass

    def all_assets(self):
        all_assets = list()
        while self.assets_layout.count():
            child = self.assets_layout.takeAt(0)
            if child.widget() is not None:
                all_assets.append(child.widget())

        return all_assets

    def clear_assets(self):
        del self.widgets[:]
        while self.assets_layout.count():
            child = self.assets_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.assets_layout.setSpacing(0)
        self.assets_layout.addStretch()

    def add_asset(self, asset):
        self.widgets.append(asset)
        self.assets_layout.insertWidget(0, asset)
        self.updateHierarchy.emit()

    def update_menu(self):
        add_layout_action = QAction('Layout', self.assets_menu)
        add_anim_action = QAction('Animation', self.assets_menu)
        add_fx_action = QAction('FX', self.assets_menu)
        add_light_action = QAction('Lighting', self.assets_menu)
        for action in [add_layout_action, add_anim_action, add_fx_action, add_light_action]:
            self.assets_menu.addAction(action)

        add_layout_action.triggered.connect(self._on_add_layout)
        add_anim_action.triggered.connect(self._on_add_animation)
        add_fx_action.triggered.connect(self._on_add_fx)
        add_light_action.triggered.connect(self._on_add_lighting)

    def _on_add_layout(self):
        res = sp.dcc.select_file_dialog(
            title='Select Layout File',
            start_directory=sp.get_solstice_project_path(),
            pattern='Layout Files (*.layout)'
        )
        if not res:
            return

        new_layout_asset = ShotAsset(asset=res)
        self.add_asset(new_layout_asset)

    def _on_add_animation(self):
        pass

    def _on_add_fx(self):
        pass

    def _on_add_lighting(self):
        pass


class NodeAsset(AbstractItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, name, params, parent=None):
        self.name = name
        self.params = params

        asset_path = self.params.get('path', None)
        self.node = None
        if asset_path:
            self.node = solstice_node.SolsticeAssetNode(name=os.path.basename(asset_path))

        super(NodeAsset, self).__init__(name, parent)

    def custom_ui(self):
        super(NodeAsset, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

        self.asset_lbl = QLabel(self.name)
        self.item_layout.addWidget(self.asset_lbl, 0, 1, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

    def get_asset_path(self):
        if not self.node:
            return

        return self.node.asset_path


class ShotHierarchy(QWidget, object):

    updateProperties = Signal(QObject)
    refresh = Signal()

    def __init__(self, parent=None):
        super(ShotHierarchy, self).__init__(parent=parent)

        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.hierarchy_layout = QVBoxLayout()
        self.hierarchy_layout.setContentsMargins(1, 1, 1, 1)
        self.hierarchy_layout.setSpacing(0)
        self.hierarchy_layout.addStretch()
        scroll_widget.setLayout(self.hierarchy_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        pass

    def all_hierarchy(self):
        all_hierarhcy = list()
        while self.hierarchy_layout.count():
            child = self.hierarchy_layout.takeAt(0)
            if child.widget() is not None:
                all_hierarhcy.append(child.widget())

        return all_hierarhcy

    def clear_hierarchy(self):
        del self.widgets[:]
        while self.hierarchy_layout.count():
            child = self.hierarchy_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.assets_layout.setSpacing(0)
        self.assets_layout.addStretch()

    def add_asset(self, asset):
        self.widgets.append(asset)
        self.hierarchy_layout.insertWidget(0, asset)
        asset.clicked.connect(self._on_item_clicked)

    def add_node(self, node_name, node_params):
        new_node = NodeAsset(
            name=node_name,
            params=node_params
        )
        self.add_asset(new_node)

    def _on_item_clicked(self, widget, event):
        if widget is None:
            self.updateProperties(None)
            return
        if sp.dcc.object_exists(widget.asset):
            for asset_widget in self.widgets:
                if asset_widget != widget:
                    asset_widget.deselect()
                else:
                    asset_widget.select()
            self.updateProperties.emit(widget)
            # widget.set_select(item_state)
        else:
            self._on_refresh_hierarchy()
            self.updateProperties.emit(None)

    def _on_refresh_hierarchy(self):
        self.clear_hierarchy()
        # self.init_ui()
        self.refresh.emit()


class AssetProperties(QWidget, object):
    def __init__(self, parent=None):
        super(AssetProperties, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        img_layout = QHBoxLayout()
        img_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(img_layout)
        img_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.prop_img = QLabel()
        self.prop_img.setPixmap(solstice_resource.pixmap('solstice_logo', category='images').scaled(QSize(125, 125), Qt.KeepAspectRatio))
        img_layout.addWidget(self.prop_img)
        img_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())


        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.props_layout = QVBoxLayout()
        self.props_layout.setContentsMargins(1, 1, 1, 1)
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()
        scroll_widget.setLayout(self.props_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)


class ShotOverrides(QWidget, object):
    def __init__(self, parent=None):
        super(ShotOverrides, self).__init__(parent=parent)

        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

        self.update_menu()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.add_btn = QPushButton('Add Override')
        self.main_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.overrides_menu = QMenu()
        self.add_btn.setMenu(self.overrides_menu)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.assets_layout = QVBoxLayout()
        self.assets_layout.setContentsMargins(1, 1, 1, 1)
        self.assets_layout.setSpacing(0)
        self.assets_layout.addStretch()
        scroll_widget.setLayout(self.assets_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        pass

    def update_menu(self):
        add_property_override = QAction('Property', self.overrides_menu)
        add_shader_override = QAction('Shader', self.overrides_menu)
        add_shader_property_override = QAction('Shader Property', self.overrides_menu)
        add_box_bbox = QAction('Box Bounding Box', self.overrides_menu)
        for action in [add_property_override, add_shader_override, add_shader_property_override, add_box_bbox]:
            self.overrides_menu.addAction(action)

        add_property_override.triggered.connect(self._on_add_property_override)
        add_shader_override.triggered.connect(self._on_add_shader_override)
        add_shader_property_override.triggered.connect(self._on_add_shader_property_override)
        add_box_bbox.triggered.connect(self._on_add_area_curve_override)

    def _on_add_property_override(self):
        pass

    def _on_add_shader_override(self):
        pass

    def _on_add_shader_property_override(self):
        pass

    def _on_add_area_curve_override(self):
        pass


class ShotAssembler(solstice_windows.Window, object):
    name = 'SolsticeShotAssembler'
    title = 'Solstice Tools - Shot Assembler'
    version = '1.0'

    def __init__(self):
        super(ShotAssembler, self).__init__()

    def custom_ui(self):
        super(ShotAssembler, self).custom_ui()

        # self.set_logo('solstice_standinmanager_logo')

        self.resize(900, 850)

        self.main_layout.setAlignment(Qt.AlignTop)

        # Menu bar
        menubar_widget = QWidget()
        menubar_layout = QVBoxLayout()
        menubar_widget.setLayout(menubar_layout)
        menubar = QMenuBar()
        file_menu = menubar.addMenu('File')
        self.load_action = QAction('Load', menubar_widget)
        file_menu.addAction(self.load_action)
        menubar_layout.addWidget(menubar)
        self.main_layout.addWidget(menubar_widget)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        self.dock_window = solstice_windows.DockWindow(use_scroll=True)
        self.dock_window.centralWidget().show()
        self.main_layout.addWidget(self.dock_window)

        self.shot_hierarchy = ShotHierarchy()
        self.shot_assets = ShotAssets()
        self.asset_props = AssetProperties()
        self.shot_overrides = ShotOverrides()

        self.dock_window.main_layout.addWidget(self.shot_hierarchy)
        self.asset_props_dock = self.dock_window.add_dock(widget=self.asset_props, name='Properties', area=Qt.RightDockWidgetArea)
        self.shot_overrides_dock = self.dock_window.add_dock(widget=self.shot_overrides, name='Overrides', area=Qt.RightDockWidgetArea)
        self.shot_assets_dock = self.dock_window.add_dock(widget=self.shot_assets, name='Assets', tabify=False, area=Qt.LeftDockWidgetArea)

        self.generate_btn = QPushButton('GENERATE SHOT')
        self.generate_btn.setMinimumHeight(30)
        self.generate_btn.setMinimumWidth(80)
        generate_layout = QHBoxLayout()
        generate_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        generate_layout.addWidget(self.generate_btn)
        generate_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addLayout(generate_layout)

        self.shot_assets.updateHierarchy.connect(self._on_update_hierarchy)
        self.shot_hierarchy.updateProperties.connect(self._on_update_properties)

    def _on_update_hierarchy(self):
        for asset in self.shot_assets.all_assets():
            asset_path = asset.asset
            if not os.path.isfile(asset_path):
                continue
            # TODO: Instead of using the extension we should check the asset object type
            if asset_path.endswith('.layout'):
                self._add_layout_asset(asset)
            elif asset_path.endswith('.anim'):
                self._add_animation_asset(asset)
            elif asset_path.endswith('.fx'):
                self._add_fx_asset(asset)

    def _add_layout_asset(self, asset):
        asset_path = asset.asset
        if not os.path.isfile(asset_path):
            sp.logger.warning('Impossible to add Layout asset because Layout File {} does not exists!'.format(asset_path))
            return

        try:
            with open(asset_path) as f:
                asset_data = json.load(f)
        except Exception as e:
            sp.logger.error(e)
            return

        for obj, params in asset_data.items():
            self.shot_hierarchy.add_node(node_name=obj, node_params=params)

    def _add_animation_asset(self, asset):
        asset_path = asset.asset
        if not os.path.isfile(asset_path):
            sp.logger.warning('Impossible to add Animation asset because Layout File {} does not exists!'.format(asset_path))
            return

        try:
            with open(asset_path) as f:
                asset_data = json.load(f)
        except Exception as e:
            sp.logger.error(e)
            return

        print(asset_data)

    def _add_fx_asset(self, asset):
        asset_path = asset.asset
        if not os.path.isfile(asset_path):
            sp.logger.warning(
                'Impossible to add FX asset because Layout File {} does not exists!'.format(asset_path))
            return

        try:
            with open(asset_path) as f:
                asset_data = json.load(f)
        except Exception as e:
            sp.logger.error(e)
            return

        print(asset_data)

    def _on_update_properties(self, asset_widget):
        if not asset_widget:
            return

        if isinstance(asset_widget, NodeAsset):
            self._on_update_node_properties(asset_widget)

    def _on_update_node_properties(self, node_asset):
        asset_icon = node_asset.node.get_icon()
        if asset_icon:
            self.asset_props.prop_img.setPixmap(QPixmap.fromImage(img.base64_to_image(asset_icon[0].encode('utf-8'), image_format=asset_icon[1])).scaled(200, 200, Qt.KeepAspectRatio))


def run():
    win = ShotAssembler().show()
    return win
