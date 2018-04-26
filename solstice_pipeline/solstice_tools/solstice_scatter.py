#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_scatter.py
# by Tomas Poveda
# Tool to scatter elements in a Maya scene
# ______________________________________________________________________
# ==================================================================="""

import os
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import maya.cmds as cmds

from solstice_gui import solstice_windows, solstice_assetviewer, solstice_splitters
from solstice_tools import solstice_pipelinizer

from solstice_gui import solstice_asset

# ======================================================================================
ScatterContextID = 'ScatterContext'

# ======================================================================================

class ScatterContext(object):
    def __init__(self, options=None, transform=None, source=None, target=None):
        """
        Setup paint context
        :param options:
        :param transform:
        :param source:
        :param target:
        """

        if cmds.draggerContext(ScatterContextID, exists=True):
            cmds.deleteUI(ScatterContextID)
        cmds.draggerContext(
            ScatterContextID,
            pressCommand=self._on_press,
            dragCommand=self._on_drag,
            releaseCommand=self._on_release,
            name=ScatterContextID,
            cursor='crossHair',
            undoMode='step')

        print('Dragger context created ....')


    def _on_press(self):
        print('Pressing')

    def _on_drag(self):
        print('Dragging')

    def _on_release(self):
        print('Releasing')






class SolsticeScatter(solstice_windows.Window, object):

    title = 'Solstice Tools - Scatter Tool'
    version = '1.0'
    docked = False

    def __init__(self, name='ScatterWindow', parent=None, **kwargs):

        self._current_asset = None
        self._context = None

        super(SolsticeScatter, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticeScatter, self).custom_ui()

        self.set_logo('solstice_scatter_logo')

        scatter_splitter = QSplitter(Qt.Horizontal)
        scatter_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(scatter_splitter)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        categories_widget.setLayout(categories_layout)
        scatter_splitter.addWidget(categories_widget)

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
            update_asset_info_fn=None,
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

        scatter_layout.addWidget(solstice_splitters.Splitter('OBJECTS  TO  SCATTER'))
        self._scatter_objects_list = QListView()
        scatter_layout.addWidget(self._scatter_objects_list)

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
        paint_btn = QPushButton('Paint')
        paint_layout.addWidget(paint_btn)

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

        # =================================================================================

        paint_btn.clicked.connect(self._scatter_context_callback)

    def _update_items(self, category, flag):
        self._current_asset = None
        self._asset_viewer.update_items(category)

    def _scatter_context_callback(self, *args):
        """
        The context callback used to scatter objects
        """

        # if args[0] == 'Paint':
        self._context = ScatterContext()






def run():
    reload(solstice_asset)
    reload(solstice_assetviewer)

    SolsticeScatter().run()
