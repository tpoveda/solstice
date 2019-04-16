#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to create shots on the fly
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json
import string

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.core import asset, node
from solstice.pipeline.gui import window, splitters, attributes
from solstice.pipeline.utils import image as img
from solstice.pipeline.resources import resource

from solstice.pipeline.tools.shotexporter import shotexporter
from solstice.pipeline.tools.alembicmanager import alembicmanager
from solstice.pipeline.tools.shaderlibrary import shaderlibrary


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

    updateHierarchy = Signal(QObject)

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

        self.add_btn = QPushButton('Add Asset File')
        self.main_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(splitters.SplitterLayout())
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
        for i in range(self.assets_layout.count()):
            child = self.assets_layout.itemAt(i)
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
        self.updateHierarchy.emit(asset)

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
        res = sp.dcc.select_file_dialog(
            title='Select Animation File',
            start_directory=sp.get_solstice_project_path(),
            pattern='Animation Files (*.anim)'
        )
        if not res:
            return

        new_anim_asset = ShotAsset(asset=res)
        self.add_asset(new_anim_asset)

    def _on_add_fx(self):
        pass

    def _on_add_lighting(self):
        pass


class NodeAsset(AbstractItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, uuid, name, path, params, parent=None):
        self.name = name
        self._uuid = uuid
        self._params = params

        self.node = None
        if path:
            self.node = node.SolsticeAssetNode(name=os.path.basename(path))

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

    def get_attributes(self):
        if not self.node:
            return {}
        return self._params

    def get_icon(self):
        if not self.node:
            return

        return self.node.get_icon()

    def reference_alembic(self):
        if not self.node:
            return

        self.node.reference_alembic_file()


class AnimAsset(AbstractItemWidget, object):
    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, uuid, name, path, params, abc_params, anim_file, parent=None):
        self.name = name
        self._path = path
        self._uuid = uuid
        self._params = params
        self._abc_params = abc_params
        self._anim_file = anim_file

        print('Anim File: {}'.format(anim_file))

        # In animations we try to retrieve the assets from the asset name
        self.node = None
        short_name = sp.dcc.node_short_name(self.name).rstrip(string.digits)
        if short_name:
            self.node = node.SolsticeAssetNode(name=short_name)
            print(self.node.get_asset_data_path())

        super(AnimAsset, self).__init__(name, parent)

    def custom_ui(self):
        super(AnimAsset, self).custom_ui()

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

    def get_attributes(self):
        if not self.node:
            return {}
        return self._params

    def get_icon(self):
        if not self.node:
            return

        return self.node.get_icon()

    def reference_animation(self):
        if not self._path:
            sp.logger.warning('Impossible to reference animation {}'.format(self._name))
            return
        anim_path = os.path.join(sp.get_solstice_project_path(), self._path)
        if not os.path.isfile(anim_path) or not anim_path.endswith(sp.DataExtensions.ABC):
            sp.logger.warning('File {} is not a valid Alembic animation file!'.format(anim_path))
            return

        if self.node:
            local_max_versions = self.node.get_local_versions()
            if not local_max_versions['model']:
                sp.logger.warning('Alembic Animation File {} is pointing to a non published asset!'.format(self.name))
        else:
            sp.logger.warning('Alembic Animation File {} is not linked to any Solstice Asset!'.format(self.name))

        if sp.is_houdini():
            alembicmanager.AlembicImporter.import_alembic(anim_path)
        else:
            alembicmanager.AlembicImporter.reference_alembic(anim_path, namespace=os.path.splitext(os.path.basename(self._anim_file))[0])


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
        for i in range(self.hierarchy_layout.count()):
            child = self.hierarchy_layout.itemAt(i)
            if child.widget() is not None:
                all_hierarhcy.append(child.widget())

        return all_hierarhcy

    def clear_hierarchy(self):
        del self.widgets[:]
        while self.hierarchy_layout.count():
            child = self.hierarchy_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.hierarchy_layout.setSpacing(0)
        self.hierarchy_layout.addStretch()

    def add_asset(self, asset):
        self.widgets.append(asset)
        self.hierarchy_layout.insertWidget(0, asset)
        asset.clicked.connect(self._on_item_clicked)

        return asset

    def add_layout(self, node_id, node_name, node_path, node_params):
        new_layout = NodeAsset(
            uuid=node_id,
            name=node_name,
            path=node_path,
            params=node_params
        )

        return self.add_asset(new_layout)

    def add_animation(self, anim_id, anim_name, anim_path, anim_params, abc_params, anim_file):
        new_anim = AnimAsset(
            uuid=anim_id,
            name=anim_name,
            path=anim_path,
            params=anim_params,
            abc_params=abc_params,
            anim_file=anim_file
        )

        return self.add_asset(new_anim)

    def _on_item_clicked(self, widget, event):
        if widget is None:
            self.updateProperties.emit(None)
            return
        else:
            for asset_widget in self.widgets:
                if asset_widget != widget:
                    asset_widget.deselect()
                else:
                    asset_widget.select()
            self.updateProperties.emit(widget)


class AssetProperties(QWidget, object):
    def __init__(self, parent=None):
        super(AssetProperties, self).__init__(parent=parent)

        self._current_asset = None
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

        img_layout = QHBoxLayout()
        img_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(img_layout)
        img_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.prop_img = QLabel()
        self.prop_img.setPixmap(resource.pixmap('solstice_logo', category='images').scaled(QSize(125, 125), Qt.KeepAspectRatio))
        self.prop_lbl = splitters.Splitter('Solstice')
        img_layout.addWidget(self.prop_img)
        img_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self. main_layout.addWidget(self.prop_lbl)

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

    def setup_signals(self):
        pass

    def all_attributes(self):
        all_attrs = list()
        for i in range(self.hierarchy_layout.count()):
            child = self.hierarchy_layout.itemAt(i)
            if child.widget() is not None:
                all_attrs.append(child.widget())

        return all_attrs

    def add_attribute(self, attr_name, attr_value=None):
        if not self._current_asset:
            return

        attr_type = None
        if attr_value is not None:
            attr_type = type(attr_value)

        if attr_type:
            if attr_type in [unicode, str, basestring]:
                new_attr = attributes.StringAttribute(node=self._current_asset, attr_name=attr_name, attr_value=attr_value)
            elif attr_type is float:
                new_attr = attributes.FloatAttribute(node=self._current_asset, attr_name=attr_name, attr_value=attr_value)
            else:
                new_attr = attributes.BaseAttributeWidget(node=self._current_asset, attr_name=attr_name, attr_value=attr_value)
        else:
            new_attr = attributes.BaseAttributeWidget(node=self._current_asset, attr_name=attr_name)
        new_attr.hide_check()
        new_attr.lock()
        self.widgets.append(new_attr)
        self.props_layout.insertWidget(0, new_attr)

        return new_attr

    def update_attributes(self, asset_widget):
        self.clear_properties()
        self._current_asset = asset_widget

    def clear_properties(self):
        del self.widgets[:]
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()


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
        self.main_layout.addLayout(splitters.SplitterLayout())
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


class ShotAssembler(window.Window, object):
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
        self.save_action = QAction('Save', menubar_widget)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        menubar_layout.addWidget(menubar)
        self.main_layout.addWidget(menubar_widget)
        self.main_layout.addLayout(splitters.SplitterLayout())

        self.dock_window = window.DockWindow(use_scroll=True)
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
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addLayout(generate_layout)

        self.shot_assets.updateHierarchy.connect(self._on_update_hierarchy)
        self.shot_hierarchy.updateProperties.connect(self._on_update_properties)
        self.generate_btn.clicked.connect(self._on_generate_shot)

    def _on_update_hierarchy(self, shot_asset):
        for asset in self.shot_assets.all_assets():
            asset_path = asset.asset
            if not os.path.isfile(asset_path):
                continue
            # TODO: Instead of using the extension we should check the asset object type
            if asset_path.endswith('.layout'):
                self._add_layout_asset(asset, shot_asset)
            elif asset_path.endswith('.anim'):
                self._add_animation_asset(asset, shot_asset)
            elif asset_path.endswith('.fx'):
                self._add_fx_asset(asset, shot_asset)

    def _add_layout_asset(self, asset, shot_asset):
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

        layout_data_version = asset_data['data_version']
        exporter_version = asset_data['exporter_version']
        if layout_data_version != sp.DataVersions.LAYOUT:
            sp.logger.warning('Layout Asset File {} is not compatible with current format. Please contact TD!'.format(asset_path))
            return
        if exporter_version != shotexporter.ShotExporter.version:
            sp.logger.warning('Layout Asset File {} was exported with an older version. Please contact TD!'.format(asset_path))
            return

        for node_id, node_info in asset_data['assets'].items():
            self.shot_hierarchy.add_layout(
                node_id=node_id,
                node_name=node_info['name'],
                node_path=node_info['path'],
                node_params=node_info['attrs']
            )

    def _add_animation_asset(self, asset, shot_asset):
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

        anim_data_version = asset_data['data_version']
        exporter_version = asset_data['exporter_version']
        if anim_data_version != sp.DataVersions.LAYOUT:
            sp.logger.warning(
                'Animation Asset File {} is not compatible with current format. Please contact TD!'.format(asset_path))
            return
        if exporter_version != shotexporter.ShotExporter.version:
            sp.logger.warning(
                'Animation Asset File {} was exported with an older version. Please contact TD!'.format(asset_path))
            return

        for anim_id, anim_info in asset_data['anims'].items():
            self.shot_hierarchy.add_animation(
                anim_id=anim_id,
                anim_name=anim_info['name'],
                anim_path=anim_info['path'],
                anim_params=anim_info['attrs'],
                abc_params=anim_info['abc_attrs'],
                anim_file=shot_asset.asset
            )

    def _add_fx_asset(self, asset, shot_asset):
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

    def _on_update_properties(self, asset_widget):
        if not asset_widget:
            return

        self.asset_props.update_attributes(asset_widget)

        if isinstance(asset_widget, AbstractItemWidget):
            self._on_update_node_properties(asset_widget)

    def _on_update_node_properties(self, node_asset):
        asset_icon = node_asset.get_icon()
        if asset_icon:
            self.asset_props.prop_img.setPixmap(QPixmap.fromImage(img.base64_to_image(asset_icon[0].encode('utf-8'), image_format=asset_icon[1])).scaled(200, 200, Qt.KeepAspectRatio))

        self.asset_props.prop_lbl.set_text(node_asset.name)

        for attr_name, attr_value in node_asset.get_attributes().items():
            self.asset_props.add_attribute(attr_name=attr_name, attr_value=attr_value)

    def _on_generate_shot(self):
        if not sp.is_maya():
            sp.logger.warning('Shoot generation is only available in Maya!')
            return

        import maya.cmds as cmds

        sp.dcc.new_file()

        from solstice.pipeline.utils import mayautils

        for node_asset in self.shot_hierarchy.all_hierarchy():
            track = mayautils.TrackNodes(full_path=True)
            track.load()

            if isinstance(node_asset, NodeAsset):
                node_asset.reference_alembic()
            elif isinstance(node_asset, AnimAsset):
                node_asset.reference_animation()

            res = track.get_delta()
            if node_asset.name not in res:
                sp.logger.warning('Node {} is not loaded!'.format(node_asset.name))
                continue

            for attr, attr_value in node_asset.get_attributes().items():
                if type(attr_value) is float:
                    sp.dcc.set_float_attribute_value(node=node_asset.name, attribute_name=attr, attribute_value=attr_value)

            sp.dcc.clear_selection()

        shaderlibrary.ShaderLibrary.load_scene_shaders()

        cmds.viewFit(animate=True)

def run():
    win = ShotAssembler().show()
    return win
