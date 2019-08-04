#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that implements mixin for Export List Tree Widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from solstice.pipeline.tools.shotexporter.widgets import exportlistviewmixin

reload(exportlistviewmixin)


class ExportTreeWidget(exportlistviewmixin.ExporterItemViewMixin, QTreeWidget):
    def __init__(self, *args):
        QTreeWidget.__init__(self, *args)
        exportlistviewmixin.ExporterItemViewMixin.__init__(self)

        self._header_labels = list()
        self._hidden_columns = dict()

        self.setAutoScroll(False)
        self.setMouseTracking(True)
        self.setSortingEnabled(False)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        header = self.header()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_show_header_menu)

    def header_labels(self):
        """
        Returns all the header labels
        :return: list(str)
        """

        return self._header_labels

    def selectedItem(self):
        """
        Returns the last selected non-hidden item
        :return: ExporterItem
        """

        items = self.selectedItems()
        if items:
            return items[-1]

        return None

    def selectedItems(self):
        """
        Returns all the selected items
        :return: list(ExporterItem)
        """

        items = list()
        items_ = QTreeWidget.selectedItems(self)

        return items

    def setColumHidden(self, column, value):
        """
        Set the given column to show or hide depending on the given value
        :param column: int or str
        :param value: bool
        """

        if isinstance(column, basestring):
            column = self.column_from_label(column)

        lbl = self.label_from_column(column)
        self._hidden_columns[lbl] = value

        QTreeWidget.setColumnHidden(self, column, value)

        # Make sure column is not collapsed
        width = self.columnWidth(column)
        if width < 5:
            width = 100
            self.setColumnWidth(column, width)

    def resizeColumnToContents(self, column):
        """
        Resizes the given column to the data of that column
        :param column: int or st r
        """
        width = 0
        for item in self.items():
            text = item.text(column)
            font = item.font(column)
            metrics = QFontMetricsF(font)
            text_width = metrics.width(text) + item.padding()
            width = max(width, text_width)

        self.setColumnWidth(column, width)

    def items(self):
        """
        Returns a list of all the items in the tree widget
        :return: list(TreeWidgetItem)
        """

        items = list()
        # for item in self._items():
        #     if not isi
        for item in self._items():
            items.append(item)

        return items

    def is_header_label(self, label):
        """
        Returns whether given label is a valid header label
        :param label: str
        """

        return label in self._header_labels

    def column_labels(self):
        """
        Returns all header labels for the tree widget
        :return: list(str)
        """

        return self.header_labels()

    def label_from_column(self, column):
        """
        Returns the column label for the given column
        :param column: int
        :return: str
        """
        if column is not None:
            return self.headerItem().text(column)

    def column_from_label(self, lbl):
        """
        Returns the column for the given label
        :param lbl: str
        :return: int
        """

        try:
            return self._header_labels.index(lbl)
        except ValueError:
            return -1

    def show_all_columns(self):
        """
        Shows all available columns
        """

        for column in range(self.columnCount()):
            self.setColumnHidden(column, False)

    def hide_all_columns(self):
        """
        Hide all available columns
        """

        for column in range(1, self.columnCount()):
            self.setColumnHidden(column, True)

    def update_column_hidden(self):
        """
        Updates the hidden state for all the current columns
        """

        self.show_all_columns()
        column_labels = self._hidden_columns.keys()
        for column_lbl in column_labels:
            self.setColumnHidden(column_lbl, self._hidden_columns[column_lbl])

    def _items(self):
        """
        Returns a list of all the items in the tree widget
        :return: list(TreeWidgetItem)
        """

        return self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive)

    def _create_header_menu(self, column):
        """
        Creates new header menu
        :param column: int
        :return: QMenu
        """

        menu = QMenu(self)
        lbl = self.label_from_column(column)
        action = menu.addAction('Hide "{}"'.format(lbl))
        callback = partial(self.setColumnHidden, column, True)
        action.triggered.connect(callback)
        menu.addSeparator()
        action = menu.addAction('Resize to Contents')
        callback = partial(self.resizeColumnToContents, column)
        action.triggered.connect(callback)

        return menu

    def _create_hide_column_menu(self):
        """
        Creates the hide column menu
        :return: QMenu
        """

        menu = QMenu('SHow/Hide Column', self)
        action = menu.addAction('Show All')
        action.triggered.connect(self.show_all_columns)
        action = menu.addAction('Hide All')
        action.triggered.connect(self.hide_all_columns)
        menu.addSeparator()
        for column in range(self.columnCount()):
            lbl = self.label_from_column(column)
            is_hidden = self.isColumnHidden(column)
            action = menu.addAction(lbl)
            action.setCheckable(True)
            action.setChecked(not is_hidden)
            callback = partial(self.setColumnHidden, column, not is_hidden)
            action.triggered.connect(callback)

        return menu

    def _on_show_header_menu(self, pos):
        """
        Creates and show the header menu at the cursor pos
        :return: QMenu
        """

        header = self.header()
        column = header.logicalIndexAt(pos)
        menu = self._create_header_menu(column)
        menu.addSeparator()
        submenu = self._create_hide_column_menu()
        menu.addMenu(submenu)
        menu.exec_(QCursor.pos())