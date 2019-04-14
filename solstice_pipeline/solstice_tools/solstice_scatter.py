#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_scatter.py
# by Tomas Poveda
# Tool to scatter elements in a Maya scene
# ______________________________________________________________________
# ==================================================================="""


from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_assetviewer, solstice_splitters
from solstice_pipeline.solstice_utils import solstice_mash_utils, solstice_artella_utils


class SolsticeScatter(solstice_windows.Window, object):

    name = 'Solstice_Scatter'
    title = 'Solstice Tools - Scatter Tool'
    version = '1.0'

    def __init__(self):

        self._current_asset = None
        self._context = None
        self._ignore_callbacks = False

        super(SolsticeScatter, self).__init__()

        self.add_callback(OpenMaya.MEventMessage.addEventCallback('NewSceneOpened', self._update_ui, self))
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SceneOpened', self._update_ui, self))
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SceneImported', self._update_ui, self))
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('NameChanged', self._update_ui, self))
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('Undo', self._update_ui, self))
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._update_ui, self))
        self.add_callback(OpenMaya.MDGMessage.addNodeRemovedCallback(self._update_ui))

        orig_sel = cmds.ls(sl=True)
        scatter_grp = 'SOLSTICE_SCATTER'
        if not cmds.objExists(scatter_grp):
            self._scatter_grp = cmds.group(empty=True, name=scatter_grp, world=True)
        else:
            self._scatter_grp = cmds.ls(scatter_grp)[0]
        cmds.select(orig_sel)

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

        asset_viewer_layout = QVBoxLayout()
        asset_viewer_layout.setContentsMargins(2, 2, 2, 2)
        asset_viewer_layout.setSpacing(2)
        main_categories_menu_layout.addLayout(asset_viewer_layout)

        self._asset_viewer = solstice_assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=self._on_asset_click,
            simple_assets=True,
            checkable_assets=True,
            show_only_published_assets=False)
            # show_only_published_assets=True)      # TODO: Uncomment later
        self._asset_viewer.setColumnCount(2)
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        asset_viewer_layout.addWidget(self._asset_viewer)
        asset_viewer_layout.addLayout(solstice_splitters.SplitterLayout())
        self._update_scatter_btn = QPushButton('Update Scatter')
        self._update_scatter_btn.setEnabled(False)
        asset_viewer_layout.addWidget(self._update_scatter_btn)

        self._categories_btn_group = QButtonGroup(self)
        self._categories_btn_group.setExclusive(True)
        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            new_btn = QPushButton(category)
            # new_btn.toggled.connect(partial(self._update_items, category))
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

        mash_list_layout = QHBoxLayout()
        mash_list_buttons_layout = QVBoxLayout()
        mash_list_buttons_layout.setAlignment(Qt.AlignTop)
        mash_list_layout.setContentsMargins(2, 2, 2, 2)
        self._mash_outliner = solstice_mash_utils.get_mash_outliner_tree()
        mash_list_layout.addWidget(self._mash_outliner)
        mash_list_layout.setSpacing(2)
        self._mash_add_btn = QToolButton()
        self._mash_add_btn.setText('+')
        self._mash_add_btn.setMinimumWidth(30)
        self._mash_add_btn.setMinimumHeight(30)
        self._mash_remove_btn = QToolButton()
        self._mash_remove_btn.setText('-')
        self._mash_remove_btn.setMinimumWidth(30)
        self._mash_remove_btn.setMinimumHeight(30)
        mash_list_layout.addLayout(mash_list_buttons_layout)
        mash_list_buttons_layout.addWidget(self._mash_add_btn)
        mash_list_buttons_layout.addWidget(self._mash_remove_btn)
        scatter_layout.addLayout(mash_list_layout)

        # create_action_menu.addAction(create_ctrl_from_selection_action)

        self._mash_add_menu = QMenu(self)
        self._mash_add_btn.setMenu(self._mash_add_menu)
        self._mash_add_btn.setPopupMode(QToolButton.InstantPopup)

        self._mash_arnold_buildin_action = QAction('Arnold Buildins', self._mash_add_menu)
        self._mash_add_menu.addAction(self._mash_arnold_buildin_action)

        for btn in [self._mash_add_btn, self._mash_remove_btn]:
            btn.setStyleSheet(
                '''
                QToolButton::menu-indicator
                { 
                    image: none;
                }
                QToolButton
                {
                    background-color: rgb(93, 93, 93);
                }
                ''')

        scatter_buttons_layout = QHBoxLayout()
        scatter_buttons_layout.setContentsMargins(2, 2, 2, 2)
        scatter_buttons_layout.setSpacing(2)
        scatter_layout.addLayout(solstice_splitters.SplitterLayout())
        scatter_layout.addLayout(scatter_buttons_layout)
        self._bake_all_scatters = QPushButton('Bake All Scatters')
        self._bake_selected_scatters = QPushButton('Bake Selected Scatters')
        self._bake_all_scatters.setEnabled(False)
        self._bake_selected_scatters.setEnabled(False)
        scatter_buttons_layout.addWidget(self._bake_selected_scatters)
        scatter_buttons_layout.addWidget(self._bake_all_scatters)

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

        # =================================================================================

        self._mash_outliner.clicked.connect(self._on_mash_outliner_click)
        # self._mash_add_btn.clicked.connect(self._add_mash)
        self._mash_remove_btn.clicked.connect(self._remove_mash)

        # =================================================================================

        self._update_ui()

    def get_selected_mash_network(self):
        item = self._mash_outliner._getCorrespondingItem(self._mash_outliner.currentIndex())
        if not item:
            return None
        return solstice_mash_utils.get_mash_network(item.getName())

    def _on_asset_click(self, asset):
        mash_network = self.get_selected_mash_network()
        if mash_network is None:
            return

        instancer = mash_network.instancer
        if instancer is None or instancer == '':
            return

        curr_sel = cmds.ls(sl=True)
        instancer_type = cmds.objectType(instancer)
        cmds.select(instancer)
        if instancer_type == 'MASH_Repro':
            repro_widget = solstice_mash_utils.get_repro_object_widget(instancer)
            if not repro_widget:
                return

            print(asset.is_published())


        elif instancer_type == 'MASH_Instancer':
            print('Add asset to MASH_Instancer')
        cmds.select(curr_sel)

    def _update_asset_viewer_ui(self, w):
        mash_network = self.get_selected_mash_network()
        print(mash_network)

        # if not mash_network:
        #     return
        # mash_scatter_data = ScatterMetaData.get_scatter_data_from_mash_network(mash_network)
        # if not mash_scatter_data:
        #     return
        #
        # scatter_nodes = cmds.getAttr(mash_scatter_data+'.scatter_nodes')
        # if scatter_nodes is None or scatter_nodes == '':
        #     return
        # else:
        #     scatter_nodes = scatter_nodes.split()
        #
        # # Firt we disable all the items
        # for i in range(self._asset_viewer.rowCount()):
        #     for j in range(self._asset_viewer.columnCount()):
        #         self._asset_viewer.cellWidget(i, j).containedWidget._asset_btn.setChecked(False)
        #
        # for node in scatter_nodes:
        #     for i in range(self._asset_viewer.rowCount()):
        #         for j in range(self._asset_viewer.columnCount()):
        #             item = self._asset_viewer.cellWidget(i, j)
        #             asset = item.containedWidget
        #             if asset.name == node:
        #                 asset._asset_btn.setChecked(True)

    def _on_mash_outliner_click(self, index):
        item = self._mash_outliner.model().itemFromIndex(index)
        is_waiter = item.mashNode.isWaiter
        self._categories_widget.setEnabled(is_waiter)
        self._mash_remove_btn.setEnabled(is_waiter)

    # def test(self, index):
    #     item = self._mash_outliner.model().itemFromIndex(index)
    #     print(item)
    #
    # def is_paint_mode(self):
    #     return self._paint_btn.isChecked()
    #
    # def _update_paint_mode(self):
    #     self._categories_widget.setEnabled(not self.is_paint_mode())
    #
    #     if self.is_paint_mode():
    #         print('We need to get selected assets and connect them to the selected MASH node')
    #     else:
    #         pass
    #
    # def _update_items(self, category, flag):
    #     self._current_asset = None
    #     self._asset_viewer.update_items(category)

    # def _add_mash_data(self):
    #     self._node = cmds.createNode('network', name=mash_network.networkName + '_scatter_data')
    #     cmds.addAttr(self._node, ln='mash_network', at='message')
    #     if not cmds.attributeQuery('scatter_data', node=mash_network.networkName, exists=True):
    #         cmds.addAttr(mash_network.networkName, ln='scatter_data', at='message')
    #     cmds.connectAttr(self._node + '.mash_network', mash_network.networkName + '.scatter_data')
    #
    #     for attr in ['scatter_nodes', 'scatter_properties']:
    #         cmds.addAttr(self._node, ln=attr, dt='string')

    def _update_ui(self, *args, **kwargs):
        mash_network = self.get_selected_mash_network()
        if not mash_network:
            self._categories_widget.setEnabled(False)
        else:
            self._categories_widget.setEnabled(True)

        if sp.dcc.get_version() <= 2017:
            self._mash_outliner.updateModel()
        else:
            self._mash_outliner.populateItems()

    def _add_mash(self):
        mash_network = solstice_mash_utils.create_mash_network()
        painter = mash_network.addNode('MASH_Placer')
        if sp.dcc.get_version() <= 2017:
            self._mash_outliner.updateModel()
        else:
            self._mash_outliner.populateItems()
        return mash_network

    def _remove_mash(self):
        mash_network = self.get_selected_mash_network()
        instancer = mash_network.instancer
        self._mash_outliner._deleteNode()
        if sp.dcc.get_version() <= 2017:
            self._mash_outliner.updateModel()
        else:
            self._mash_outliner.populateItems()
        if instancer and cmds.objExists(instancer):
            cmds.delete(instancer)


def run():
    # Check that Artella plugin is loaded and, if not, we loaded it
    solstice_artella_utils.update_artella_paths()
    if not solstice_artella_utils.check_artella_plugin_loaded():
        if not solstice_artella_utils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    sp.update_solstice_project_path()

    win = SolsticeScatter().show()

    return win
