#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_filelistwidget.py
# by Tomas Poveda
# Module that includes widget classes to work with files and folders
# The browser can be based on real folder structure or JSON dict folder
# structure
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *


class FileListWidget(QListWidget, object):
    def __init__(self, parent):
        self.parent = parent
        super(FileListWidget, self).__init__(parent=parent)

        self.itemSelectionChanged.connect(self.select_item)
        self.itemDoubleClicked.connect(self.activate_item)

    def wheelEvent(self, event):
        """
        Overrides QWidget wheelEvent to smooth scroll bar movement
        :param event: QWheelEvent
        """

        sb = self.horizontalScrollBar()
        min_value = sb.minimum()
        max_value = sb.maximum()
        if sb.isVisible() and max_value > min_value:
            sb.setValue(sb.value() + (-1 if event.delta() > 0 else 1))
        super(FileListWidget, self).wheelEvent(event)

    def keyPressEvent(self, event):
        """
        Overrides QWidget keyPressEvent with some shortcuts when using the widget
        :param event:
        :return:
        """
        modifiers = event.modifiers()
        if event.key() == int(Qt.Key_Return) and modifiers == Qt.NoModifier:
            if len(self.selectedItems()) > 0:
                item = self.selectedItems()[0]
                if item.type() == 0:  # directory
                    self.directory_activated.emit(item.text())
                else:  # file
                    self.file_activated.emit(item.text())
        elif event.key() == int(Qt.Key_Backspace) and modifiers == Qt.NoModifier:
            self.up_requested.emit()
        elif event.key() == int(Qt.Key_F5) and modifiers == Qt.NoModifier:
            self.update_requested.emit()
        else:
            super(FileListWidget, self).keyPressEvent(event)

    def select_item(self):
        if len(self.selectedItems()) > 0:
            item = self.selectedItems()[0]
            if item.type() == 0:  # directory
                self.folder_selected.emit(item.text())
            if item.type() == 1:  # file
                self.file_selected.emit(item.text())

    def activate_item(self):
        if len(self.selectedItems()) > 0:
            item = self.selectedItems()[0]
            if item.type() == 0:  # directory
                self.directory_activated.emit(item.text())
            else:  # file
                self.file_activated.emit(item.text())

    def set_extended_selection(self):
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.disconnect(self.select_item)
        self.itemSelectionChanged.connect(self.process_selection_changed)

    def process_selection_changed(self):
        """
        Gets all selected items and emits a proper signal with the proper selected item names
        """

        items = filter(lambda x: x.type() != 0, self.selectedItems())
        names = map(lambda x: x.text(), items)
        self.files_selected.emit(names)
