#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base definition for export list widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.gui import base, search, buttons

from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.widgets import exportreewidget

reload(defines)
reload(search)
reload(exportreewidget)


class TreeWidget(QTreeWidget, object):
    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent=parent)

        self.setHeaderHidden(True)
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(
            '''
            QTreeView{alternate-background-color: #3b3b3b;}
            QTreeView::item {padding:3px;}
            QTreeView::item:!selected:hover {
                background-color: #5b5b5b;
                margin-left:-3px;
                border-left:0px;
            }
            QTreeView::item:selected {
                background-color: #48546a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            QTreeView::item:selected:hover {
                background-color: #586c7a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            '''
        )

    def mousePressEvent(self, event):
        item = self.indexAt(event.pos())
        selected = self.selectionModel().isSelected(item)
        super(TreeWidget, self).mousePressEvent(event)
        if item.row() == -1 and item.column() == -1 or selected:
            self.clearSelection()
            index = QModelIndex()
            self.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)


class BaseExportList(base.BaseWidget, object):

    ExportType = 'EXPORT'
    IconMode = 'icon'
    TableMode = 'table'

    itemClicked = Signal(object)
    refresh = Signal()

    def __init__(self, parent=None):
        super(BaseExportList, self).__init__(parent=parent)

    def custom_ui(self):
        super(BaseExportList, self).custom_ui()

        self.setMouseTracking(True)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        self.main_layout.addLayout(top_layout)

        self.refresh_btn = buttons.IconButton('refresh', icon_padding=2, parent=self)
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        # self.new_item_btn = buttons.IconButton(icon_name='plus', icon_hover='plus_hover')

        top_layout.addWidget(self.refresh_btn)
        self.controls_filter = search.SearchFindWidget(parent=self)
        top_layout.addWidget(self.controls_filter)

        self.assets_list = TreeWidget(parent=self)
        self.main_layout.addWidget(self.assets_list)

        self.controls_filter.textChanged.connect(self._on_filter_assets_list)
        self.assets_list.itemSelectionChanged.connect(lambda: self.itemClicked.emit(self.assets_list.selectedItems()))

    def setup_signals(self):
        self.refresh_btn.clicked.connect(self._on_refresh_exporter)

    def init_ui(self):
        """
        Function that is called during initialization
        Override in custom export lists
        """

        pass

    def clear_exporter_list(self):
        self.assets_list.clear()

    def refresh_exporter(self):
        self._on_refresh_exporter()

    def _on_filter_assets_list(self, filter_text):
        """
        This function is called each time the user enters text in the search line widget
        Shows or hides elements in the list taking in account the filter_text
        :param filter_text: str, current text
        """

        for i in range(self.assets_list.topLevelItemCount()):
            item = self.assets_list.topLevelItem(i)
            item.setHidden(filter_text not in item.text(0))

    def _on_refresh_exporter(self):
        self.clear_exporter_list()
        self.init_ui()
        self.refresh.emit()

    def count(self):
        root = self.assets_list.invisibleRootItem()
        return root.childCount()

    def item_at(self, index):
        root = self.assets_list.invisibleRootItem()
        if index < 0 or index > self.count() - 1:
            return None

        return root.child(index)

    def asset_at(self, index):
        item = self.item_at(index)
        if not item:
            return None

        return item.asset


    # def all_widgets(self):
    #     all_widgets = list()
    #     while self.exporter_layout.count():
    #         child = self.exporter_layout.takeAt(0)
    #         if child.widget() is not None:
    #             all_widgets.append(child.widget())
    #
    #     return all_widgets
    #
    # def append_widget(self, asset):
    #     self.widgets.append(asset)
    #     self.exporter_layout.insertWidget(0, asset)
    #
    # def remove_widget(self, asset):
    #     pass