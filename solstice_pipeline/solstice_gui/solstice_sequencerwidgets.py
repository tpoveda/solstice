#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sequencer.py
# by Tomas Poveda
# This module contains widgets used in the Solstice Sequencer
# ______________________________________________________________________
# ==================================================================="""

import os

import solstice_pipeline as sp
from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

from solstice_pipeline.solstice_utils import solstice_maya_utils as utils
from solstice_pipeline.solstice_gui import solstice_splitters, solstice_sync_dialog
from solstice_utils import solstice_image as img
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella, solstice_python_utils as py_utils
from solstice_pipeline.resources import solstice_resource

reload(solstice_splitters)


class SequenceFile(QFrame, object):
    def __init__(self, status, root_path, base_path, file_path, parent=None):
        super(SequenceFile, self).__init__(parent)

        self._status = status
        self._root = root_path
        self._path = base_path
        self._file = file_path

        self.setMaximumWidth(150)

        self.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.lbl = QLabel('MASTER LAYOUT')
        self.lbl.setStyleSheet('background-color: rgb(32, 32, 32);')
        self.lbl.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl)
        main_layout.addLayout(solstice_splitters.SplitterLayout())

        main_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Expanding))

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        main_layout.addLayout(buttons_layout)
        sync_btn = QToolButton()
        sync_btn.setStatusTip('Sync File')
        sync_btn.setToolTip('Sync File')
        sync_btn.setIcon(solstice_resource.icon('sync'))
        open_btn = QToolButton()
        open_btn.setStatusTip('Open File')
        open_btn.setToolTip('Open File')
        open_btn.setIcon(solstice_resource.icon('open'))
        import_btn = QToolButton()
        import_btn.setStatusTip('Import File')
        import_btn.setToolTip('Import File')
        import_btn.setIcon(solstice_resource.icon('import'))
        reference_btn = QToolButton()
        reference_btn.setStatusTip('Reference File')
        reference_btn.setToolTip('Reference File')
        reference_btn.setIcon(solstice_resource.icon('reference'))
        new_version_btn = QToolButton()
        new_version_btn.setStatusTip('New Version')
        new_version_btn.setToolTip('New Version')
        new_version_btn.setIcon(solstice_resource.icon('upload'))

        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        buttons_layout.addWidget(sync_btn)
        buttons_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(import_btn)
        buttons_layout.addWidget(reference_btn)
        buttons_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
        buttons_layout.addWidget(new_version_btn)
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        main_layout.addItem(QSpacerItem(0, 5, QSizePolicy.Fixed, QSizePolicy.Expanding))

        sync_btn.clicked.connect(self.sync)
        open_btn.clicked.connect(self.open)

    def sync(self):
        solstice_sync_dialog.SolsticeSyncPath(paths=[self._root]).sync()

    def open(self):
        if not self._file or not os.path.isfile(self._file):
            return

        artella.open_file_in_maya(file_path=self._file)

    def import_file(self):
        if not self._file or not os.path.isfile(self._file):
            return

        artella.import_file_in_maya(file_path=self._file)

    def reference_file(self):
        if not self._file or not os.path.isfile(self._file):
            return

        artella.reference_file_in_maya(file_path=self._file)

    def new_version(self):
        if not self._file or not os.path.isfile(self._file):
            return


class SequenceWidget(QWidget, object):

    syncShots = Signal(object)

    def __init__(self, sequence_data, sequence_files=None, parent=None):
        super(SequenceWidget, self).__init__(parent=parent)

        self._sequence_data = sequence_data

        if sequence_files is None:
            sequence_files = dict()

        self._sequence_files = sequence_files

        self.custom_ui()

    @property
    def name(self):
        return self._sequence_data.name

    @property
    def path(self):
        return self._sequence_data.path

    def custom_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(2)
        widget_layout.setAlignment(Qt.AlignLeft)
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        main_frame.setLineWidth(1)
        main_frame.setLayout(widget_layout)
        main_layout.addWidget(main_frame)

        # Name and icon layout
        icon_name_layout = QVBoxLayout()
        icon_name_layout.setContentsMargins(2, 2, 2, 2)
        icon_name_layout.setSpacing(2)
        icon_name_layout.setAlignment(Qt.AlignLeft)
        widget_layout.addLayout(icon_name_layout)
        seq_lbl = solstice_splitters.Splitter(self.name)
        icon_lbl = QLabel()
        icon_name_layout.addWidget(seq_lbl)
        icon_name_layout.addWidget(icon_lbl)

        widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

        # Master Layout
        master_layout = self._sequence_files.get('master_layout', None)
        if not master_layout:
            return

        master_layout_file = SequenceFile(
            status='working',
            root_path=master_layout.get('path', None),
            base_path=master_layout['working'].get('path', None),
            file_path=master_layout['working'].get('file', None)
        )

        widget_layout.addWidget(master_layout_file)
        widget_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        open_btn = QPushButton()
        # open_btn.setText('Shots')
        open_btn.setMaximumWidth(40)
        open_btn.setIcon(solstice_resource.icon('shots'))
        open_btn.setToolTip('Load Sequence Shots')
        open_btn.setStatusTip('Load Sequence Shots')
        # open_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        open_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        widget_layout.addWidget(open_btn)

        # open_master_layout_btn.clicked.connect(self.open_master_layout)

        shot_icon = self.get_icon()
        if shot_icon:
            icon_lbl.setPixmap(shot_icon)

        open_btn.clicked.connect(self._on_open_shots)

    def mousePressEvent(self, event):
        super(SequenceWidget, self).mousePressEvent(event)

    def get_data_folder(self):
        data_folder = os.path.join(self.path, '_data')

        if not os.path.exists(data_folder):
            return

        return data_folder

    def get_icon(self):
        data_folder = self.get_data_folder()
        if data_folder:
            for root, dirs, files in os.walk(data_folder):
                if dirs and '__working__' in dirs:
                    shot_path = root
                    sequence_data_file = os.path.join(shot_path, '__working__', 'data.json')
                    if os.path.isfile(sequence_data_file):
                        sequence_data = py_utils.read_json(sequence_data_file)
                        icon = sequence_data['sequence']['icon'].encode('utf-8')
                        icon_format = sequence_data['sequence']['icon_format']
                        sequence_icon = QPixmap.fromImage(img.base64_to_image(icon, image_format=icon_format))
                        return sequence_icon
        else:
            return solstice_resource.pixmap(name='solstice_logo', extension='png')

    def _on_open_shots(self):
        self.syncShots.emit(self)


class ShotWidget(QWidget, object):
    def __init__(self, shot_data, shot_files, parent=None):
        super(ShotWidget, self).__init__(parent=parent)

        self._shot_data = shot_data
        self._shot_files = shot_files

        # ===================================================================
        self._has_previs = False
        self._has_anim = False
        self._has_fx = False
        self._has_lighting = False

        if self._shot_files:
            for file_type, file_path in self._shot_files.items():
                if not file_path:
                    continue
                if not file_path.endswith('.ma'):
                    continue
                if file_type == 'previs':
                    self._has_previs = True
                elif file_type == 'anim':
                    self._has_anim = True
                elif file_type == 'effects':
                    self._has_anim = True
                elif file_type == 'light':
                    self._has_lighting = True

        # ===================================================================

        self.custom_ui()

    @property
    def name(self):
        return self._shot_data.name

    @property
    def path(self):
        return self._shot_data.path

    def custom_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        widget_layout = QHBoxLayout()
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(2)
        widget_layout.setAlignment(Qt.AlignLeft)
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        main_frame.setLineWidth(1)
        main_frame.setLayout(widget_layout)
        main_layout.addWidget(main_frame)

        # Name and icon layout
        icon_name_layout = QVBoxLayout()
        icon_name_layout.setContentsMargins(2, 2, 2, 2)
        icon_name_layout.setSpacing(2)
        icon_name_layout.setAlignment(Qt.AlignLeft)
        widget_layout.addLayout(icon_name_layout)
        seq_lbl = solstice_splitters.Splitter(self.name)
        icon_lbl = QLabel()
        icon_name_layout.addWidget(seq_lbl)
        icon_name_layout.addWidget(icon_lbl)

        widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

        shot_icon = self.get_icon()
        if shot_icon:
            icon_lbl.setPixmap(shot_icon)

        # Previs Layout
        if self._has_previs:
            previs_layout = QVBoxLayout()
            previs_layout.setContentsMargins(2, 2, 2, 2)
            previs_layout.setSpacing(2)
            previs_layout.setAlignment(Qt.AlignLeft)
            widget_layout.addLayout(previs_layout)

            previs_layout_lbl = QLabel('- PREVIS -')
            previs_layout_lbl.setAlignment(Qt.AlignCenter)
            open_previs_btn = QPushButton('Open')
            previs_layout.addWidget(previs_layout_lbl)
            previs_layout.addLayout(solstice_splitters.SplitterLayout())
            previs_layout.addWidget(open_previs_btn)

            widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

        # Animation Layout
        if self._has_anim:
            anim_layout = QVBoxLayout()
            anim_layout.setContentsMargins(2, 2, 2, 2)
            anim_layout.setSpacing(2)
            anim_layout.setAlignment(Qt.AlignLeft)
            widget_layout.addLayout(anim_layout)

            anim_layout_lbl = QLabel('- ANIMATION -')
            anim_layout_lbl.setAlignment(Qt.AlignCenter)
            open_anim_btn = QPushButton('Open')
            anim_layout.addWidget(anim_layout_lbl)
            anim_layout.addLayout(solstice_splitters.SplitterLayout())
            anim_layout.addWidget(open_anim_btn)

            widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

        # FX Layout
        if self._has_fx:
            fx_layout = QVBoxLayout()
            fx_layout.setContentsMargins(2, 2, 2, 2)
            fx_layout.setSpacing(2)
            fx_layout.setAlignment(Qt.AlignLeft)
            widget_layout.addLayout(fx_layout)

            fx_layout_lbl = QLabel('- FX -')
            fx_layout_lbl.setAlignment(Qt.AlignCenter)
            open_fx_btn = QPushButton('Open')
            fx_layout.addWidget(fx_layout_lbl)
            fx_layout.addLayout(solstice_splitters.SplitterLayout())
            fx_layout.addWidget(open_fx_btn)

            widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

        # lighting
        if self._has_lighting:
            lighting_layout = QVBoxLayout()
            lighting_layout.setContentsMargins(2, 2, 2, 2)
            lighting_layout.setSpacing(2)
            lighting_layout.setAlignment(Qt.AlignLeft)
            widget_layout.addLayout(lighting_layout)

            lighting_layout_lbl = QLabel('- LIGHTING -')
            lighting_layout_lbl.setAlignment(Qt.AlignCenter)
            open_lighting_btn = QPushButton('Open')
            lighting_layout.addWidget(lighting_layout_lbl)
            lighting_layout.addLayout(solstice_splitters.SplitterLayout())
            lighting_layout.addWidget(open_lighting_btn)

            widget_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())

    def get_icon(self):
        for root, dirs, files in os.walk(self.path):
            if dirs and '__working__' in dirs:
                shot_path = root
                shot_data_file = os.path.join(shot_path, '__working__', 'data.json')
                if os.path.isfile(shot_data_file):
                    shot_data = py_utils.read_json(shot_data_file)
                    icon = shot_data['shot']['icon'].encode('utf-8')
                    icon_format = shot_data['shot']['icon_format']
                    shot_icon = QPixmap.fromImage(img.base64_to_image(icon, image_format=icon_format))
                    return shot_icon
        else:
            return solstice_resource.pixmap(name='solstice_logo', extension='png')



# ROW_HEIGHT = 110
#
# SEQUENCE_BAR_COLOR = Qt.UserRole + 1
# WINDOW_BACKGROUND = Qt.UserRole + 2
# BACKGROUND_COLOR = Qt.UserRole + 3
# IS_SEQUENCE = Qt.UserRole + 4
# FILE_TYPE = Qt.UserRole + 5
#
# BAR_COLOR_WIDTH = utils.dpi_scale(6)
# EXPANDED_ARROW = (utils.dpi_scale(QPointF(9.0, 11.0)), utils.dpi_scale(QPointF(19.0, 11.0)), utils.dpi_scale(QPointF(14.0, 16.0)))
# COLLAPSED_ARROW = (utils.dpi_scale(QPointF(12.0, 8.0)), utils.dpi_scale(QPointF(17.0, 13.0)), utils.dpi_scale(QPointF(12.0, 18.0)))
# ARROW_COLOR = QColor(189, 189, 189)
# EXPANDED_ARROW_OFFSET = utils.dpi_scale(10.0)
# COLLAPSED_ARROW_OFFSET = utils.dpi_scale(13.0)
# ICON_PADDING = utils.dpi_scale(10.0)
#
#
# class SequencerTreeView(QTreeView, object):
#     def __init__(self, sequences, parent=None):
#
#         super(SequencerTreeView, self).__init__(parent=parent)
#
#         self._sequences = sequences
#
#         self.setHeaderHidden(True)
#         self.setIndentation(12)
#         self.setMouseTracking(True)
#         self.setSelectionMode(QAbstractItemView.SingleSelection)
#         self.header().setCascadingSectionResizes(False)
#         self.resizeColumnToContents(0)
#         self.setExpandsOnDoubleClick(False)
#         self.setRootIsDecorated(False)
#         self.setColumnWidth(0, 250)
#         self.header().resizeSection(0, 250)
#
#         # sequence_layout = SequenceFileNode(file_name='Master Layout', icon=None, enabled=True)
#
#         root = SequencerItem(None, 'All', None, None)
#
#         self._sequence_nodes = list()
#         for seq_data, seq_files in self._sequences.items():
#             sequence = SequencerNode(sequence_name=seq_data.name, icon=None, enabled=True)
#             sequence_item = SequencerItem(sequence, sequence.name, None, root)
#             self._sequence_nodes.append(sequence_item)
#
#             for file_name, file_data in seq_files.items():
#                 seq_file = SequenceFileNode(file_name=file_name, icon=None, enabled=True)
#                 sequence_item = SequencerItem(seq_file, seq_file.name, None, sequence_item)
#
#         model = SequencerTreeModel(sequencer_view=self, root=root)
#         self.setModel(model)
#
#         delegate = SequencerDelegate(sequencer_view=self)
#         self.setItemDelegate(delegate)
#
#         self.expandAll()
#
#
# class SequencerTreeModel(QAbstractItemModel, object):
#     """
#     Data model used by Sequencer Tree
#     """
#
#     def __init__(self, sequencer_view, root=None, parent=None):
#         super(SequencerTreeModel, self).__init__(parent=parent)
#
#         self._view = weakref.ref(sequencer_view)
#
#         if not root:
#             self._root = SequencerItem(None, 'All', None, None)
#         else:
#             self._root = root
#
#         self._parents = {0 : self._root}
#         self._selected_sequence = None
#
#     def flags(self, index):
#         def_flags = QAbstractItemModel.flags(self, index)
#
#         if not index.isValid():
#             return
#
#         return Qt.ItemIsEnabled | Qt.ItemIsSelectable
#         # return def_flags
#
#     def columnCount(self, parent=None):
#         if parent and parent.isValid():
#             return parent.internalPointer().columnCount()
#         else:
#             return 1
#
#     def rowCount(self, parent=QModelIndex()):
#         # if parent.column() > 0:
#         #     return 0
#         if not parent.isValid():
#             parent_item = self._root
#         else:
#             parent_item = parent.internalPointer()
#         return parent_item.childCount()
#
#     def headerData(self, column, orientation, role):
#         if orientation == Qt.Horizontal and role == Qt.DisplayRole:
#             try:
#                 return ""
#             except IndexError:
#                 pass
#         if orientation == Qt.Horizontal and role == Qt.SizeHintRole:
#             return QSize(250, utils.dpi_scale(ROW_HEIGHT))
#
#         return None
#
#     def data(self, index, role):
#         if not index.isValid():
#              return None
#
#         item = index.internalPointer()
#
#         if role == Qt.DisplayRole:
#             return item.data(index.column())
#         elif role == Qt.SizeHintRole and index.column() == 0:
#             return QSize(250, utils.dpi_scale(ROW_HEIGHT))
#         elif role == Qt.BackgroundRole:
#             return item.data(BACKGROUND_COLOR)
#         elif role == Qt.ForegroundRole:
#             return self._view().palette().text().color()
#         elif role == Qt.FontRole:
#             font = QApplication.font()
#             return font
#         elif role == Qt.TextAlignmentRole:
#             return Qt.AlignLeft | Qt.AlignVCenter
#         elif role == SEQUENCE_BAR_COLOR:
#             return item.data(SEQUENCE_BAR_COLOR)
#         elif role == WINDOW_BACKGROUND:
#             return QColor(43, 43, 43)
#         elif role == IS_SEQUENCE:
#             return item.data(IS_SEQUENCE)
#
#     def parent(self, index):
#         if not index.isValid():
#             return QModelIndex()
#
#         child_item = index.internalPointer()
#         if not child_item:
#             return QModelIndex()
#
#         parent_item = child_item.parent()
#         if parent_item == self._root:
#             return QModelIndex()
#
#         return self.createIndex(parent_item.row(), 0, parent_item)
#
#     def index(self, row, column, parent):
#         if not self.hasIndex(row, column, parent):
#             return QModelIndex()
#
#         if not parent.isValid():
#             parent_item = self._root
#         else:
#             parent_item = parent.internalPointer()
#
#         child_item = parent_item.child(row)
#         if child_item:
#             return self.createIndex(row, column, child_item)
#         else:
#             return QModelIndex()
#
#
# class SequencerDelegate(QItemDelegate, object):
#     def __init__(self, sequencer_view):
#         super(SequencerDelegate, self).__init__()
#
#         self._view = weakref.ref(sequencer_view)
#
#     def paint(self, painter, option, index):
#         if not index.isValid():
#             return
#
#         item = index.internalPointer()
#         rect = deepcopy(option.rect)
#
#         if not item.data(IS_SEQUENCE):
#             rect.setLeft(rect.left()+50)
#
#         self._draw_background(rect, painter, option, index)
#         self._draw_color_bar(painter, rect, index)
#         self._draw_fill(painter, rect, index)
#         self._draw_arrow_drag_lock(painter, rect, index)
#         text_rect = self._draw_text(rect, painter, option, index, item)
#
#     def _draw_background(self, rect, painter, option, index):
#         old_pen = painter.pen()
#         item = index.internalPointer()
#         # if item.data(IS_SEQUENCE):
#             # if option.showDecorationSelected and option.state & QStyle.State_Selected:
#             #     painter.fillRect(rect, option.palette.color(QPalette.Highlight))
#             # else:
#             #     painter.fillRect(rect, index.data(Qt.BackgroundRole))
#
#         painter.fillRect(rect, index.data(Qt.BackgroundRole))
#
#         painter.setPen(old_pen)
#
#     def _draw_color_bar(self, painter, rect, index):
#         color = index.data(SEQUENCE_BAR_COLOR)
#         seq_rect = deepcopy(rect)
#         seq_rect.setRight(seq_rect.left() + BAR_COLOR_WIDTH)
#         painter.fillRect(seq_rect, color)
#
#     def _draw_fill(self, painter, rect, item):
#
#         seq_rect = deepcopy(rect)
#         old_pen = painter.pen()
#
#         painter.setPen(QPen(item.data(WINDOW_BACKGROUND), 2))
#         seq_rect.setLeft(seq_rect.left())
#         seq_rect.setRight(seq_rect.right() - 2)
#         seq_rect.setTop(seq_rect.top())
#         seq_rect.setBottom(seq_rect.bottom())
#         painter.drawRect(seq_rect)
#
#         painter.setPen(old_pen)
#
#     def _draw_arrow_drag_lock(self, painter, rect, item):
#         painter.save()
#         arrow = None
#
#         if item.data(IS_SEQUENCE):
#             paddºing = utils.dpi_scale(3)
#             painter.translate(rect.left()+padding, rect.top()+utils.dpi_scale(2))
#             arrow = COLLAPSED_ARROW
#             if self._view().isExpanded(item):
#                 arrow = EXPANDED_ARROW
#
#             old_brush = painter.brush()
#             painter.setBrush(ARROW_COLOR)
#             painter.setPen(Qt.NoPen)
#             painter.drawPolygon(arrow)
#             painter.setBrush(old_brush)
#             painter.restore()
#
#     def _draw_text(self, rect, painter, option, index, item):
#         old_pen = painter.pen()
#         draw_enabled = True
#         painter.setPen(QPen(index.data(Qt.ForegroundRole), 1))
#
#         painter.setFont(index.data(Qt.FontRole))
#         text_rect = deepcopy(rect)
#         text_rect.setBottom(text_rect.bottom() + utils.dpi_scale(2))
#         text_rect.setLeft(text_rect.left() + utils.dpi_scale(40) + ICON_PADDING)
#         text_rect.setRight(text_rect.right() - utils.dpi_scale(11))
#         painter.drawText(text_rect, index.data(Qt.TextAlignmentRole), index.data(Qt.DisplayRole))
#         painter.setPen(old_pen)
#         oldPen = painter.pen()
#
#         return text_rect
#
#
# class SequencerNode(object):
#     def __init__(self, sequence_name, icon, enabled):
#         self._sequence_name = sequence_name
#         self._icon = icon
#         self._enabled = enabled
#
#         self._label_color = QColor(240, 90, 90)
#         color = QColor(0, 0, 0)
#         color.setNamedColor("#444444")
#         self._background_color = color
#         self._enabled = enabled
#         self._tooltip = None
#
#     @property
#     def name(self):
#         return self._sequence_name
#
#     @property
#     def label_color(self):
#         return self._label_color
#
#     @property
#     def background_color(self):
#         return self._background_color
#     #
#     # def __repr__(self):
#     #     return 'SEQUENCE - {0}'.format(self._sequence_name)
#
#
# class SequenceFileNode(object):
#     def __init__(self, file_name, icon, enabled):
#         self._file_name = file_name
#         self._icon = icon
#         self._enabled = enabled
#
#         self._label_color = QColor(240, 90, 90)
#         color = QColor(0, 0, 0)
#         color.setNamedColor("#444444")
#         self._background_color = color
#         self._enabled = enabled
#         self._tooltip = None
#
#     @property
#     def name(self):
#         return self._file_name
#
#     @property
#     def label_color(self):
#         return self._label_color
#
#     @property
#     def background_color(self):
#         return self._background_color
#
#
# class SequencerItem(object):
#     """
#     Python object used in TreeModel to keep note of parent/child relationship
#     of all tree elements
#     """
#     def __init__(self, sequence_node, header, show_enabled, parent_item):
#         self._sequence_node = sequence_node
#         self._parent_item = parent_item
#         self._header = header
#         self._child_items = list()
#         self._connected_files = list()
#         self._show_enable = show_enabled
#
#         if parent_item is not None:
#             parent_item.appendChild(self)
#
#     @property
#     def sequence_node(self):
#         return self._sequence_node
#
#     def get_name(self):
#         if self._sequence_node:
#             return self._sequence_node.name
#         else:
#             return None
#
#     def set_name(self, name):
#         pass
#
#     def childCount(self):
#         return len(self._child_items)
#
#     def columnCount(self):
#         return 2
#
#     def rowCount(self):
#         parent = self._parent_item
#         if not parent:
#             return 0
#         return parent.childCount()
#
#     def parent(self):
#         return self._parent_item
#
#     def appendChild(self, item):
#         self._child_items.append(item)
#
#     def child(self, row):
#         if row < len(self._child_items):
#             return self._child_items[row]
#         else:
#             return None
#
#     def row(self):
#         if self._parent_item:
#             return self._parent_item._child_items.index(self)
#         return 0
#
#     def data(self, column):
#
#         if self._sequence_node is None:
#             if column == 0:
#                 return self._header
#         else:
#             if column == 0:
#                 return self._sequence_node.name
#             elif column == SEQUENCE_BAR_COLOR:
#                 return self._sequence_node.label_color
#             elif column == BACKGROUND_COLOR:
#                 return self._sequence_node.background_color
#             elif column == IS_SEQUENCE:
#                 return type(self._sequence_node) == SequencerNode
#
#         return None
#
#     def isExpanded(self, index):
#         if self._parent_item:
#             parent = self._parent_item
#             name = parent.__name__
#             return self._parent_item.is_expanded(index)
#
#     def log(self, tab_level=-1):
#         output = ""
#         tab_level += 1
#         for i in range(tab_level):
#             output += "\t"
#         output += "/------" + self.get_name() + "\n"
#         for child in self._child_items:
#             output += child.log(tab_level)
#         tab_level -= 1
#         return output
#
#     def __repr__(self):
#         return self.log()
