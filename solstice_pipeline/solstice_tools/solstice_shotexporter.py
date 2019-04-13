#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shotexporter.py
# by Tomas Poveda
# Tool to export shot elements
# ______________________________________________________________________
# ==================================================================="""

import os
import json
import collections

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters, solstice_attributes
from solstice_pipeline.resources import solstice_resource

reload(solstice_attributes)


MUST_ATTRS = [
    'worldMatrix',
    'translateX', 'translateY', 'translateZ',
    'rotateX', 'rotateY', 'rotateZ',
    'scaleX', 'scaleY', 'scaleZ']


class AbstractExportList(QWidget, object):

    updateProperties = Signal(QObject)
    refresh = Signal()

    def __init__(self, parent=None):
        super(AbstractExportList, self).__init__(parent=parent)

        self.widget_tree = collections.defaultdict(list)
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

        self.refresh_btn = QPushButton('Reload')
        self.refresh_btn.setIcon(solstice_resource.icon('refresh'))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.refresh_btn)

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

        self.exporter_layout = QVBoxLayout()
        self.exporter_layout.setContentsMargins(1, 1, 1, 1)
        self.exporter_layout.setSpacing(0)
        self.exporter_layout.addStretch()
        scroll_widget.setLayout(self.exporter_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        self.refresh_btn.clicked.connect(self._on_refresh_exporter)

    def init_ui(self):
        pass

    def all_widgets(self):
        all_widgets = list()
        while self.exporter_layout.count():
            child = self.exporter_layout.takeAt(0)
            if child.widget() is not None:
                all_widgets.append(child.widget())

        return all_widgets

    def append_widget(self, asset):
        self.widgets.append(asset)
        self.exporter_layout.insertWidget(0, asset)

    def remove_widget(self, asset):
        pass

    def refresh_exporter(self):
        self._on_refresh_exporter()

    def clear_exporter(self):
        del self.widgets[:]
        while self.exporter_layout.count():
            child = self.exporter_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        self.exporter_layout.setSpacing(0)
        self.exporter_layout.addStretch()

    def _on_refresh_exporter(self):
        self.widget_tree = collections.defaultdict(list)
        self.clear_exporter()
        self.init_ui()
        self.refresh.emit()


class AbstractExporterItemWidget(QWidget, object):
    def __init__(self, asset, parent=None):
        super(AbstractExporterItemWidget, self).__init__(parent)

        self.asset = asset
        self.parent = parent
        self.attrs = dict()

        self.setMouseTracking(True)

        self.is_selected = False

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.custom_ui()
        self.setup_signals()

        self.setMinimumHeight(35)

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
        self.is_selected = True
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(21,60,97);}')

    def deselect(self):
        self.is_selected = False
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

    def set_select(self, select=False):
        if select:
            self.select()
        else:
            self.deselect()

        return self.is_selected


class AbstractPropertiesWidget(QWidget, object):
    def __init__(self, parent=None):
        super(AbstractPropertiesWidget, self).__init__(parent=parent)

        self._current_asset = None
        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
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
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget() is not None:
                all_attrs.append(child.widget())

        return all_attrs

    def add_attribute(self, attr_name):
        if not self._current_asset:
            return

        new_attr = solstice_attributes.BaseAttributeWidget(node=self._current_asset, attr_name=attr_name)
        new_attr.toggled.connect(self._on_update_attribute)
        self.widgets.append(new_attr)
        self.props_layout.insertWidget(0, new_attr)

        return new_attr

    def update_attributes(self, asset_widget):
        if asset_widget == self._current_asset:
            return

        self.clear_properties()
        self._current_asset = asset_widget

        xform_attrs = sp.dcc.list_attributes(asset_widget.asset.name)
        for attr in xform_attrs:
            new_attr = self.add_attribute(attr)
            if self._current_asset.attrs[new_attr.name] is True:
                new_attr.check()
            else:
                new_attr.uncheck()

    def clear_properties(self):
        del self.widgets[:]
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()

    def _on_update_attribute(self, attr_name, flag):
        if not self._current_asset:
            return

        if attr_name not in self._current_asset.attrs.keys():
            sp.logger.warning('Impossible to udpate attribute {} because node {} has no that attribute!'.format(attr_name, self._current_asset.asset))
            return

        self._current_asset.attrs[attr_name] = flag


class ExporterAssetItem(AbstractExporterItemWidget, object):

    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, asset, parent=None):
        super(ExporterAssetItem, self).__init__(asset, parent)

        self._update_attrs()

    def custom_ui(self):
        super(ExporterAssetItem, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

        self.asset_lbl = QLabel(self.asset.name)
        self.item_layout.addWidget(self.asset_lbl, 0, 1, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

    def _update_attrs(self):
        if self.attrs:
            return

        xform_attrs = sp.dcc.list_attributes(self.asset.name)
        for attr in xform_attrs:
            if attr in MUST_ATTRS:
                self.attrs[attr] = True
            else:
                self.attrs[attr] = False


class LayoutExportList(AbstractExportList, object):

    def __init__(self, parent=None):
        super(LayoutExportList, self).__init__(parent=parent)

    def init_ui(self):
        assets = sp.get_assets()
        for asset in assets:
            asset_widget = ExporterAssetItem(asset)
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()
            asset_widget.clicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, widget, event):
        if widget is None:
            self.updateProperties(None)
            return

        if sp.dcc.object_exists(widget.asset.name):
            for asset_widget, file_items in self.widget_tree.items():
                if asset_widget != widget:
                    asset_widget.deselect()
                else:
                    asset_widget.select()
            self.updateProperties.emit(widget)
            # widget.set_select(item_state)
        else:
            self._on_refresh_exporter()
            self.updateProperties.emit(None)


class LayoutPropertiesWidget(AbstractPropertiesWidget, object):
    def __init__(self, parent=None):
        super(LayoutPropertiesWidget, self).__init__(parent=parent)


class LayoutExporter(QWidget, object):
    def __init__(self, parent=None):
        super(LayoutExporter, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.exporter_list = LayoutExportList()
        self.props_list = LayoutPropertiesWidget()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        main_splitter.addWidget(self.exporter_list)
        main_splitter.addWidget(self.props_list)

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        self.save_btn = QPushButton('SAVE LAYOUT')
        self.save_btn.setMinimumHeight(30)
        self.save_btn.setMinimumWidth(80)
        save_layout = QHBoxLayout()
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        save_layout.addWidget(self.save_btn)
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addLayout(save_layout)

    def setup_signals(self):
        self.exporter_list.updateProperties.connect(self._on_update_properties)
        self.exporter_list.refresh.connect(self._on_clear_properties)
        self.save_btn.clicked.connect(self._on_save)

    def init_ui(self):
        self.exporter_list.init_ui()

    def _on_update_properties(self, asset_widget):
        if asset_widget and sp.dcc.object_exists(asset_widget.asset.name):
            self.props_list.update_attributes(asset_widget)
        else:
            sp.logger.warning('Impossible to update properties because object {} does not exists!'.format(asset_widget.asset))
            self.props_list.clear_properties()

    def _on_clear_properties(self):
        self.props_list.clear_properties()

    def _on_save(self):
        scene_name = sp.dcc.scene_name()
        if not scene_name:
            scene_name = 'undefined'

        export_path = os.path.join('D:/solstice', scene_name+'.layout')

        layout_info = dict()
        for w in self.exporter_list.all_widgets():
            asset_name = w.asset.name
            layout_info[asset_name] = dict()
            layout_info[asset_name]['path'] = os.path.relpath(w.asset.asset_path, sp.get_solstice_project_path())
            layout_info[asset_name]['attrs'] = dict()
            for attr, flag in w.attrs.items():
                if not flag and attr not in MUST_ATTRS:
                    continue
                attr_value = sp.dcc.get_attribute_value(node=asset_name, attribute_name=attr)
                layout_info[asset_name]['attrs'][attr] = attr_value

        try:
            with open(export_path, 'w') as f:
                json.dump(layout_info, f)
        except Exception as e:
            sp.logger.error(str(e))


class AnimationExporter(QWidget, object):
    def __init__(self, parent=None):
        super(AnimationExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.reload_btn = QPushButton('RELOAD')
        self.main_layout.addWidget(self.reload_btn)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())


class FXExporter(QWidget, object):
    def __init__(self, parent=None):
        super(FXExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.reload_btn = QPushButton('RELOAD')
        self.main_layout.addWidget(self.reload_btn)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())


class ShotExporter(solstice_windows.Window, object):
    name = 'SolsticeShotExporter'
    title = 'Solstice Tools - Shot Exporter'
    version = '1.0'

    def __init__(self):
        super(ShotExporter, self).__init__()

    def custom_ui(self):
        super(ShotExporter, self).custom_ui()

        # self.set_logo('solstice_standinmanager_logo')

        self.resize(550, 650)

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.layout_exporter = LayoutExporter()
        self.anim_exporter = AnimationExporter()
        self.fx_exporter = AnimationExporter()

        self.main_tabs.addTab(self.layout_exporter, 'Layout')
        self.main_tabs.addTab(self.anim_exporter, 'Animation')
        self.main_tabs.addTab(self.fx_exporter, 'FX')

        self.layout_exporter.init_ui()

    #     self.main_tabs.currentChanged.connect(self._on_change_tab)
    #
    # def _on_change_tab(self, tab_index):
    #     if tab_index == 1:
    #         self.alembic_exporter.refresh()




def run():
    win = ShotExporter().show()
    return win
