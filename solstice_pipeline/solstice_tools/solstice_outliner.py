#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_outliner.py
# by Tomas Poveda
# Tool used to show assets related with Solstice
# ______________________________________________________________________
# ==================================================================="""

import weakref

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

from solstice_gui import solstice_windows


class OutlinerListView(QListView, object):
    def __init__(self, parent=None):
        super(OutlinerListView, self).__init__(parent=parent)

        # self.setMouseTracking(True)
        # self.setDragEnabled(True)
        # self.setAcceptDrops(True)
        # self.setDropIndicatorShown(True)
        # self.setDefaultDropAction(Qt.MoveAction)
        # self.setSelectionMode(QAbstractItemView.SingleSelection)

        model_data = [1, 2, 3, 4]
        model = OutlinerListModel(model_data)
        self.setModel(model)

        delegate = OutlinerListViewDelegate(outliner_view=self)
        self.setItemDelegate(delegate)

    def update_model(self):
        pass


class OutlinerListViewDelegate(QItemDelegate, object):
    def __init__(self, outliner_view):
        super(OutlinerListViewDelegate, self).__init__()
        self.outliner_view = weakref.ref(outliner_view)

    def paint(self, painter, option, index):
        painter.save()

        # set background color
        painter.setPen(QPen(Qt.NoPen))
        if option.state & QStyle.State_Selected:
            painter.setBrush(QBrush(Qt.red))
        else:
            painter.setBrush(QBrush(Qt.white))
        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QPen(Qt.black))
        value = index.data(Qt.DisplayRole)
        text = str(value)
        painter.drawText(option.rect, Qt.AlignLeft, text)

        painter.restore()


class OutlinerListItem(object):
    def __init__(self, node, parent_item):
        self.node = node
        self.parent_item = parent_item


class OutlinerListModel(QAbstractListModel):
    def __init__(self, colors=[], parent=None):
        super(OutlinerListModel, self).__init__(parent)
        self._items = colors

    def rowCount(self, parent):
        return len(self._items)

    def data(self, index, role):
        if role == Qt.EditRole:
            return self._items[index.row()]
        if role == Qt.DisplayRole:
            row = index.row()
            value = self._items[row]
            return value

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self._items.insert(position, 0)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            value = self._items[position]
            self._items.remove(value)
        self.endRemoveRows()
        return True


class SolsticeOutliner(solstice_windows.Window, object):

    name = 'Solstice_Outliner'
    title = 'Solstice Tools - Outliner'
    version = '1.0'
    docked = True

    def __init__(self, name='OutlinerWindow', parent=None, **kwargs):
        super(SolsticeOutliner, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticeOutliner, self).custom_ui()

        self.set_logo('solstice_outliner_logo')

        self.outliner = OutlinerListView()
        self.main_layout.addWidget(self.outliner)

        self.register_callbacks()

    def register_callbacks(self):
        pass
        # self.add_callback(OpenMaya.MEventMessage.addEventCallback('NewSceneOpened', self.update_outliner, self))
        # self.add_callback(OpenMaya.MEventMessage.addEventCallback('SceneOpened', self.update_outliner, self))
        # self.add_callback(OpenMaya.MEventMessage.addEventCallback('SceneImported', self.update_outliner, self))
        # self.add_callback(OpenMaya.MEventMessage.addEventCallback('NameChanged', self.update_outliner, self))
        # self.add_callback(OpenMaya.MEventMessage.addEventCallback('Undo', self.update_outliner, self))
        # self.add_callback(OpenMaya.MDGMessage.addNodeRemovedCallback(self.update_outliner))

    def update_outliner(self):
        print('Updating Outliner ...')
        # self.cleanup()
        # if self.outliner:
        #     self.register_callbacks()
        #     self.outliner.update_model()


def run():
    SolsticeOutliner.run()