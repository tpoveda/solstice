#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_scatter.py
# by Tomas Poveda
# Tool to scatter elements in a Maya scene
# ______________________________________________________________________
# ==================================================================="""

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

from solstice_gui import solstice_windows, solstice_assetviewer, solstice_splitters
from solstice_tools import solstice_pipelinizer
from solstice_utils import solstice_mash_utils

from solstice_gui import solstice_asset


class ScatterMetaData(object):
    def __init__(self, mash_network):
        self._mash_network = mash_network
        self._scatter_nodes = list()
        self._scatter_properties = dict()

        self._node = cmds.createNode('network', name=mash_network.networkName+'_scatter_data')
        cmds.addAttr(self._node, ln='mash_network', at='message')
        if not cmds.attributeQuery('scatter_data', node=mash_network.networkName, exists=True):
            cmds.addAttr(mash_network.networkName, ln='scatter_data', at='message')
        cmds.connectAttr(self._node+'.mash_network', mash_network.networkName+'.scatter_data')

        for attr in ['scatter_nodes', 'scatter_properties']:
            cmds.addAttr(self._node, ln=attr, dt='string')

    def add_scatter_node(self, node_name):
        pass

    def remove_scatter_node(self, node_name):
        pass

    @staticmethod
    def get_scatter_data_from_mash_network(mash_network):
        try:
            return cmds.listConnections(mash_network.networkName + '.scatter_data')[0]
        except:
            return None


class SolsticeScatter(solstice_windows.Window, object):

    title = 'Solstice Tools - Scatter Tool'
    version = '1.0'
    docked = False

    def __init__(self, name='ScatterWindow', parent=None, **kwargs):

        self._current_asset = None
        self._context = None
        self._ignore_callbacks = False

        super(SolsticeScatter, self).__init__(name=name, parent=parent, **kwargs)

        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._update_ui))

    def custom_ui(self):
        super(SolsticeScatter, self).custom_ui()

        self.set_logo('solstice_scatter_logo')

        scatter_splitter = QSplitter(Qt.Horizontal)
        scatter_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(scatter_splitter)

        self._categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        self._categories_widget.setLayout(categories_layout)
        scatter_splitter.addWidget(self._categories_widget)

        main_categories_menu_layout = QHBoxLayout()
        main_categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        main_categories_menu_layout.setSpacing(0)
        categories_layout.addLayout(main_categories_menu_layout)

        categories_menu = QWidget()
        categories_menu_layout = QVBoxLayout()
        categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        categories_menu_layout.setSpacing(0)
        categories_menu_layout.setAlignment(Qt.AlignTop)
        categories_menu.setLayout(categories_menu_layout)
        main_categories_menu_layout.addWidget(categories_menu)

        self._asset_viewer = solstice_assetviewer.AssetViewer(
            assets_path=solstice_pipelinizer.Pipelinizer.get_solstice_assets_path(),
            item_prsesed_callback=self._update_scatter_node,
            simple_assets=True,
            checkable_assets=True)
        self._asset_viewer.setColumnCount(2)
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_categories_menu_layout.addWidget(self._asset_viewer)

        self._categories_btn_group = QButtonGroup(self)
        self._categories_btn_group.setExclusive(True)
        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            new_btn = QPushButton(category)
            new_btn.toggled.connect(partial(self._update_items, category))
            categories_buttons[category] = new_btn
            categories_buttons[category].setCheckable(True)
            categories_menu_layout.addWidget(new_btn)
            self._categories_btn_group.addButton(new_btn)
        categories_buttons['All'].setChecked(True)

        scatter_widget = QWidget()
        scatter_layout = QVBoxLayout()
        scatter_layout.setContentsMargins(5, 5, 5, 5)
        scatter_layout.setSpacing(5)
        scatter_widget.setLayout(scatter_layout)
        scatter_splitter.addWidget(scatter_widget)

        scatter_layout.addWidget(solstice_splitters.Splitter('TARGET SURFACES'))
        self._target_surfaces_list = QListView()
        scatter_layout.addWidget(self._target_surfaces_list)

        v_div_w = QWidget()
        v_div_l = QHBoxLayout()
        v_div_l.setAlignment(Qt.AlignCenter)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v_div.setFrameShape(QFrame.HLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        scatter_layout.addWidget(v_div_w)

        scatter_layout.addWidget(solstice_splitters.Splitter('TRANSFORM'))
        scatter_transform_widget = QWidget()
        scatter_transform_layout = QVBoxLayout()
        scatter_widget.setLayout(scatter_transform_layout)

        v_div_w = QWidget()
        v_div_l = QHBoxLayout()
        v_div_l.setAlignment(Qt.AlignCenter)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v_div.setFrameShape(QFrame.HLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        scatter_layout.addWidget(v_div_w)

        scatter_layout.addWidget(solstice_splitters.Splitter('PAINT'))
        paint_widget = QWidget()
        paint_layout = QVBoxLayout()
        paint_layout.setContentsMargins(5, 5, 5, 5,)
        paint_layout.setSpacing(5)
        paint_widget.setLayout(paint_layout)
        scatter_layout.addWidget(paint_widget)
        self._paint_btn = QPushButton('Paint')
        self._paint_btn.setCheckable(True)
        paint_layout.addWidget(self._paint_btn)

        scatter_layout.addWidget(solstice_splitters.Splitter('PAINT_OPTIONS'))
        paint_options_widget = QWidget()
        paint_options_layout = QVBoxLayout()
        paint_options_layout.setContentsMargins(5, 5, 5, 5, )
        paint_options_layout.setSpacing(5)
        paint_options_widget.setLayout(paint_options_layout)
        scatter_layout.addWidget(paint_options_widget)

        v_div_w = QWidget()
        v_div_l = QHBoxLayout()
        v_div_l.setAlignment(Qt.AlignCenter)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v_div.setFrameShape(QFrame.HLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        scatter_layout.addWidget(v_div_w)

        mash_splitter = QSplitter(Qt.Horizontal)
        mash_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scatter_splitter.addWidget(mash_splitter)

        mash_widget = QWidget()
        mash_layout = QVBoxLayout()
        mash_widget.setLayout(mash_layout)
        mash_splitter.addWidget(mash_widget)

        mash_list_layout = QHBoxLayout()
        mash_list_buttons_layout = QVBoxLayout()
        mash_list_buttons_layout.setAlignment(Qt.AlignTop)
        mash_list_layout.setContentsMargins(2, 2, 2, 2)
        mash_list_layout.setSpacing(2)
        mash_add_btn = QPushButton('+')
        mash_add_btn.setMinimumWidth(30)
        mash_add_btn.setMinimumHeight(30)
        mash_remove_btn = QPushButton('-')
        mash_remove_btn.setMinimumWidth(30)
        mash_remove_btn.setMinimumHeight(30)
        mash_list_buttons_layout.addWidget(mash_add_btn)
        mash_list_buttons_layout.addWidget(mash_remove_btn)
        mash_layout.addLayout(mash_list_layout)
        self._mash_list = QListView()
        self._mash_list_model = QStringListModel()
        self._mash_list.setModel(self._mash_list_model)
        mash_list_layout.addWidget(self._mash_list)
        mash_list_layout.addLayout(mash_list_buttons_layout)
        mash_tree = solstice_mash_utils.get_mash_outliner_tree()
        mash_list_layout.addWidget(mash_tree)

        # =================================================================================

        self._mash_list.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self._mash_list_model.dataChanged.connect(self._rename_mash)
        mash_add_btn.clicked.connect(self._add_mash)
        mash_remove_btn.clicked.connect(self._remove_mash)
        self._paint_btn.toggled.connect(self._update_paint_mode)

        # =================================================================================

        self._update_ui()

    def is_paint_mode(self):
        return self._paint_btn.isChecked()

    def _update_paint_mode(self):
        self._categories_widget.setEnabled(not self.is_paint_mode())

        if self.is_paint_mode():
            print('We need to get selected assets and connect them to the selected MASH node')
        else:
            pass





    def _update_items(self, category, flag):
        self._current_asset = None
        self._asset_viewer.update_items(category)

    def _add_mash(self):
        mash_network = solstice_mash_utils.create_mash_network()
        return ScatterMetaData(mash_network=mash_network)

    def _rename_mash(self, index):
        sel_indices = self._mash_list.selectionModel().selection().indexes()
        if len(sel_indices) > 0:
            item = sel_indices[0]
            cmds.rename(cmds.ls(sl=True)[0], item.data())

    def _remove_mash(self):
        sel_indices = self._mash_list.selectionModel().selection().indexes()
        if len(sel_indices) > 0:
            item = sel_indices[0]
            solstice_mash_utils.remove_mash_network(item.data())
            self._mash_list.selectionModel().setCurrentIndex(self._mash_list_model.index(self._mash_list_model.rowCount()-1), QItemSelectionModel.Select)

    def _update_mash_list(self):

        new_selection = cmds.ls(sl=True)
        if len(new_selection) > 0:
            new_selection = new_selection[0]
        else:
            new_selection = None

        self._mash_list_model.removeRows(0, self._mash_list_model.rowCount())
        mash_waiters = solstice_mash_utils.get_mash_nodes()
        for m in mash_waiters:
            if self._mash_list_model.insertRow(self._mash_list_model.rowCount()):
                index = self._mash_list_model.index(self._mash_list_model.rowCount()-1, 0)
                self._mash_list_model.setData(index, m)
                if new_selection and m == new_selection:
                    self._mash_list.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)

    def _on_selection_changed(self):
        self._update_mash_selection()
        self._update_asset_viewer_ui()

    def _update_mash_selection(self, index=None):
        sel_indices = self._mash_list.selectionModel().selection().indexes()
        if len(sel_indices) > 0:
            self._categories_widget.setEnabled(True)
            item = sel_indices[0]
            if cmds.objExists(item.data()):
                self._ignore_callbacks = True
                cmds.select(item.data(), replace=True, noExpand=True)
                self._ignore_callbacks = False
        else:
            self._categories_widget.setEnabled(False)

        self._update_asset_viewer_ui()

    def _update_ui(self, *args, **kwargs):
        if not self._ignore_callbacks:
            self._update_mash_selection()
            self._update_mash_list()

    def get_selected_mash_network(self):
        sel_indices = self._mash_list.selectionModel().selection().indexes()
        if len(sel_indices) > 0:
            item = sel_indices[0]
            if item:
                item_data = item.data()
                print(item_data)
                try:
                    return solstice_mash_utils.get_mash_network(item_data)
                except:
                    pass
        return None

    def _update_asset_viewer_ui(self):
        mash_network = self.get_selected_mash_network()
        if not mash_network:
            return
        mash_scatter_data = ScatterMetaData.get_scatter_data_from_mash_network(mash_network)
        if not mash_scatter_data:
            return

        scatter_nodes = cmds.getAttr(mash_scatter_data+'.scatter_nodes')
        if scatter_nodes is None or scatter_nodes == '':
            return
        else:
            scatter_nodes = scatter_nodes.split()

        # Firt we disable all the items
        for i in range(self._asset_viewer.rowCount()):
            for j in range(self._asset_viewer.columnCount()):
                self._asset_viewer.cellWidget(i, j).containedWidget._asset_btn.setChecked(False)

        for node in scatter_nodes:
            for i in range(self._asset_viewer.rowCount()):
                for j in range(self._asset_viewer.columnCount()):
                    item = self._asset_viewer.cellWidget(i, j)
                    asset = item.containedWidget
                    if asset.name == node:
                        asset._asset_btn.setChecked(True)

    def _update_scatter_node(self, asset):
        if not asset:
            return
        mash_network = self.get_selected_mash_network()
        if not mash_network:
            return
        mash_scatter_data = ScatterMetaData.get_scatter_data_from_mash_network(mash_network)
        if not mash_scatter_data:
            return

        asset_name = asset.name
        asset_check = asset._asset_btn.isChecked()

        if asset_check:
            scatter_nodes = cmds.getAttr(mash_scatter_data+'.scatter_nodes')
            if scatter_nodes is None or scatter_nodes == '':
                scatter_nodes = asset_name
            else:
                scatter_nodes_split = scatter_nodes.split()
                if asset_name in scatter_nodes_split:
                    return
                scatter_nodes_split.append(asset_name)
                scatter_nodes = ''.join(str(s) + ' ' for s in scatter_nodes_split)
            cmds.setAttr(mash_scatter_data+'.scatter_nodes', scatter_nodes, type='string')
        else:
            scatter_nodes = cmds.getAttr(mash_scatter_data+'.scatter_nodes')
            if scatter_nodes is None or scatter_nodes == '':
                return
            scatter_nodes_split = scatter_nodes.split()
            if asset_name in scatter_nodes_split:
                scatter_nodes_split.remove(asset_name)
            else:
                return
            scatter_nodes = ''.join(str(s) + ' ' for s in scatter_nodes_split)
            cmds.setAttr(mash_scatter_data+'.scatter_nodes', scatter_nodes, type='string')

        self._update_asset_viewer_ui()


def run():
    reload(solstice_asset)
    reload(solstice_assetviewer)
    reload(solstice_mash_utils)

    SolsticeScatter().run()
