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
import collections

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

from solstice_pipeline.solstice_utils import solstice_node, solstice_maya_utils, solstice_qt_utils
from solstice_pipeline.solstice_gui import solstice_messagehandler
from solstice_pipeline.resources import solstice_resource

global solstice_outliner_window


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


class SolsticeOutliner(QWidget, object):

    name = 'SolsticeOutliner'
    title = 'Solstice Outliner'
    version = '1.0'

    instances = list()

    def __init__(self, parent=solstice_maya_utils.get_maya_window()):
        super(SolsticeOutliner, self).__init__(parent=parent)

        SolsticeOutliner._delete_instances()
        self.__class__.instances.append(weakref.proxy(self))
        cmds.select(clear=True)

        self.assets = list()

        self.custom_ui()
        self.setup_signals()

        global solstice_outliner_window
        solstice_outliner_window = self

    def custom_ui(self):

        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.parent().layout().addLayout(self.main_layout)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(solstice_resource.icon('refresh'))
        self.refresh_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.main_layout.addWidget(self.refresh_btn, 0, 0, 1, 1)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(scroll_widget)

        self.assets_layout = QVBoxLayout()
        self.assets_layout.setContentsMargins(1, 1, 1, 1)
        self.assets_layout.setSpacing(0)
        # self.assets_layout.addStretch()
        scroll_widget.setLayout(self.assets_layout)
        self.main_layout.addWidget(scroll_area, 1, 0, 1, 3)

        self.outliner = OutlinerListView()
        self.assets_layout.addWidget(self.outliner)

        self.register_callbacks()

    def setup_signals(self):
        pass

    # ==========================================================================================================

    @staticmethod
    def _delete_instances():
        for ins in SolsticeOutliner.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
            except Exception:
                pass

            SolsticeOutliner.instances.remove(ins)
            del ins

    # ==========================================================================================================

    def append_asset(self, asset):
        self.assets.append(asset)
        self.assets_layout.insertWidget(0, asset)

    def remove_asset(self, asset):
        pass

    def clear_assets(self):
        del self.assets[:]
        while self.assets_layout.count():
            child = self.assets_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()

        # self.assets_layout.setSpacing(0)
        # self.assets_layout.addStretch()

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

    # ==========================================================================================================

    def run(self):
        return self


class SolsticeOutlinerManager(object):
    def __init__(self):
        self.widget_tree = collections.defaultdict(list)

        self.ui = SolsticeOutliner()
        self.io = solstice_messagehandler.MessageHandler()
        self.callbacks = OpenMaya.MCallbackIdArray()

        self.custom_ui()
        self.setup_signal()

    def custom_ui(self):
        pass

    def setup_signal(self):
        pass

    # ==========================================================================================================

    def add_callbacks(self):
        pass

    def remove_callbacks(self):
        pass

    # ==========================================================================================================

    @staticmethod
    def get_tag_data_nodes():
        tag_nodes = list()
        objs = cmds.ls()
        for obj in objs:
            valid_tag_data = cmds.attributeQuery('tag_type', node=obj, exists=True)
            if valid_tag_data:
                tag_type = cmds.getAttr(obj + '.tag_type')
                if tag_type and tag_type == 'SOLSTICE_TAG':
                    tag_node = solstice_node.SolsticeTagDataNode(node=obj)
                    tag_nodes.append(tag_node)

        return tag_nodes

    # ==========================================================================================================

    def _on_selection_changed(self):
        pass

    def _on_refresh_outliner(self):
        pass

    # ==========================================================================================================

    def show(self):
        self.add_callbacks()
        self._on_refresh_outliner()
        self.ui.show()


def run():
    solstice_qt_utils.dock_window(SolsticeOutliner)
