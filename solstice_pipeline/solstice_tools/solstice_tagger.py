#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tagger.py
# by Tomas Poveda
# Tool used to manage metadata for each asset in Solstice Short Film
# ______________________________________________________________________
# ==================================================================="""

import os
from functools import partial

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

from solstice_gui import solstice_windows, solstice_grid, solstice_buttons, solstice_label
from solstice_utils import solstice_python_utils as utils
from resources import solstice_resource


class TaggerWidget(QWidget, object):
    def __init__(self, type_title_name, type_name, type_category, type_image=None, parent=None):
        super(TaggerWidget, self).__init__(parent=parent)

        self._type_title_name = type_title_name
        self._type_name = type_name
        self._type_image = type_image
        self._type_category = type_category

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self.btn = QPushButton(type_title_name)
        self.btn.setCheckable(True)
        main_layout.addWidget(self.btn)

        type_lbl = QLabel(type_title_name)
        type_lbl.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(type_lbl)

    def get_name(self):
        return self._type_name

    def get_category(self):
        return self._type_category


class SolsticeTagger(solstice_windows.Window, object):

    name = 'Solstice_Tagger'
    title = 'Solstice Tools - Tagger'
    version = '1.0'
    docked = False

    tag_attributes = ['types', 'selections', 'description']

    def __init__(self, name='TaggerWindow', parent=None, **kwargs):

        super(SolsticeTagger, self).__init__(name=name, parent=parent, **kwargs)
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed, self))

    def custom_ui(self):
        super(SolsticeTagger, self).custom_ui()

        self.set_logo('solstice_tagger_logo')

        self._error_pixmap = solstice_resource.pixmap('error', category='icons').scaled(QSize(24, 24))
        self._warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
        self._ok_pixmap = solstice_resource.pixmap('ok', category='icons').scaled(QSize(24, 24))

        self._curr_selection = 'scene'

        tagger_editor_layout = QVBoxLayout()
        tagger_editor_layout.setContentsMargins(0, 0, 0, 0)
        tagger_editor_layout.setSpacing(0)
        tagger_editor_widget = QWidget()
        tagger_editor_widget.setLayout(tagger_editor_layout)
        self.main_layout.addWidget(tagger_editor_widget)

        tagger_info_widget = QWidget()
        tagger_info_widget.setMaximumHeight(60)
        tagger_info_widget.setMinimumHeight(60)
        tagger_info_layout = QHBoxLayout()
        tagger_info_layout.setContentsMargins(0, 0, 0, 0)
        tagger_info_layout.setSpacing(0)
        tagger_info_layout.setAlignment(Qt.AlignTop)
        tagger_info_widget.setLayout(tagger_info_layout)
        tagger_editor_layout.addWidget(tagger_info_widget)

        curr_selection_widget = QWidget()
        curr_selection_layout = QHBoxLayout()
        curr_selection_layout.setContentsMargins(20, 20, 20, 20)
        curr_selection_layout.setSpacing(0)
        curr_selection_widget.setLayout(curr_selection_layout)
        tagger_info_layout.addWidget(curr_selection_widget)
        self._curr_selection_lbl = QLabel(self._curr_selection)
        self._curr_selection_lbl.setAlignment(Qt.AlignCenter)
        curr_selection_layout.addWidget(self._curr_selection_lbl)

        v_div_w = QWidget()
        v_div_l = QVBoxLayout()
        v_div_l.setAlignment(Qt.AlignLeft)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setMinimumHeight(30)
        v_div.setFrameShape(QFrame.VLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        tagger_info_layout.addWidget(v_div_w)

        curr_info_widget = QWidget()
        curr_info_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        curr_info_layout = QHBoxLayout()
        curr_info_layout.setContentsMargins(5, 5, 5, 5)
        curr_info_layout.setSpacing(0)
        curr_info_widget.setLayout(curr_info_layout)
        tagger_info_layout.addWidget(curr_info_widget)

        self._curr_info_image = QLabel()
        self._curr_info_image.setPixmap(self._error_pixmap)
        curr_info_layout.addWidget(self._curr_info_image)
        v_div_w = QWidget()
        v_div_l = QVBoxLayout()
        v_div_l.setAlignment(Qt.AlignLeft)
        v_div_l.setContentsMargins(5, 5, 5, 5)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setMaximumHeight(30)
        v_div.setFrameShape(QFrame.VLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        curr_info_layout.addWidget(v_div_w)
        self._curr_info_lbl = QLabel('')
        self._curr_info_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._curr_info_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        curr_info_layout.addWidget(self._curr_info_lbl)

        # ======================================================================================

        self._tagger_widgets = QStackedWidget(self)
        tagger_editor_layout.addWidget(self._tagger_widgets)

        self._new_tagger_node_widget = QWidget()
        new_tagger_node_layout = QVBoxLayout()
        new_tagger_node_layout.setContentsMargins(35, 5, 35, 5)
        new_tagger_node_layout.setSpacing(5)
        self._new_tagger_node_widget.setLayout(new_tagger_node_layout)
        self._new_tagger_node_btn = QPushButton('Create Tag Data node for "{0}"?'.format(self._curr_selection))
        new_tagger_node_layout.addWidget(self._new_tagger_node_btn)
        self._tagger_widgets.addWidget(self._new_tagger_node_widget)

        self._tagger_tabs = QTabWidget()
        self._tagger_widgets.addWidget(self._tagger_tabs)

        self._type_editor_widget = QWidget()
        type_editor_layout = QVBoxLayout()
        type_editor_layout.setContentsMargins(0, 0, 0, 0)
        type_editor_layout.setSpacing(0)
        self._type_editor_widget.setLayout(type_editor_layout)
        self._type_grid = solstice_grid.GridWidget()
        self._type_grid.setShowGrid(False)
        self._type_grid.setColumnCount(4)
        self._type_grid.horizontalHeader().hide()
        self._type_grid.verticalHeader().hide()
        self._type_grid.resizeRowsToContents()
        self._type_grid.resizeColumnsToContents()
        type_editor_layout.addWidget(self._type_grid)
        self._tagger_tabs.addTab(self._type_editor_widget, 'Type')

        self._selection_editor_widget = QWidget()
        selection_editor_layout = QVBoxLayout()
        selection_editor_layout.setContentsMargins(0, 0, 0, 0)
        selection_editor_layout.setSpacing(0)
        self._selection_editor_widget.setLayout(selection_editor_layout)
        self._selection_grid = solstice_grid.GridWidget()
        self._selection_grid.setShowGrid(False)
        self._selection_grid.setColumnCount(4)
        self._selection_grid.horizontalHeader().hide()
        self._selection_grid.verticalHeader().hide()
        self._selection_grid.resizeRowsToContents()
        self._selection_grid.resizeColumnsToContents()
        selection_editor_layout.addWidget(self._selection_grid)
        self._tagger_tabs.addTab(self._selection_editor_widget, 'Selections')

        self._high_low_editor_widget = QWidget()
        high_low_editor_layout = QVBoxLayout()
        high_low_editor_layout.setContentsMargins(0, 0, 0, 0)
        high_low_editor_layout.setSpacing(0)
        self._high_low_editor_widget.setLayout(high_low_editor_layout)
        high_layout = QHBoxLayout()
        high_lbl = QLabel('High: ')
        self.high_line = solstice_label.DragDropLine()
        high_layout.addWidget(high_lbl)
        high_layout.addWidget(self.high_line)
        high_low_editor_layout.addLayout(high_layout)
        low_layout = QHBoxLayout()
        low_lbl = QLabel('Proxy: ')
        self.low_line = solstice_label.DragDropLine()
        low_layout.addWidget(low_lbl)
        low_layout.addWidget(self.low_line)
        high_low_editor_layout.addLayout(low_layout)
        self._tagger_tabs.addTab(self._high_low_editor_widget, 'High/Proxy')

        self._description_editor_widget = QWidget()
        description_editor_layout = QVBoxLayout()
        description_editor_layout.setContentsMargins(0, 0, 0, 0)
        description_editor_layout.setSpacing(0)
        self._description_editor_widget.setLayout(description_editor_layout)
        self._description_text = QTextEdit()
        description_editor_layout.addWidget(self._description_text)
        self._tagger_tabs.addTab(self._description_editor_widget, 'Description')

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        self.main_layout.addLayout(bottom_layout)
        select_tag_data_btn = QPushButton('Select Tag Data')
        remove_tag_data_btn = QPushButton('Remove Tag Data')
        bottom_layout.addWidget(select_tag_data_btn)
        bottom_layout.addWidget(remove_tag_data_btn)

        # ================================================================================

        self._description_text.textChanged.connect(partial(self.update_tag_data_info, 'description', None, None))
        self._new_tagger_node_btn.clicked.connect(self._update_metadata_node_for_curr_selection)
        select_tag_data_btn.clicked.connect(self._select_tag_data_node)
        remove_tag_data_btn.clicked.connect(self._remove_tag_data_node)

        # ================================================================================

        self._update_types()
        self._on_selection_changed()

    def _select_tag_data_node(self):
        tag_data_node = self.get_tag_data_node_from_curr_sel()
        if tag_data_node is None:
            return
        cmds.select(tag_data_node)

    def _remove_tag_data_node(self):
        tag_data_node = self.get_tag_data_node_from_curr_sel()
        if tag_data_node is None:
            return
        cmds.delete(tag_data_node)
        self.update_metadata_node()
        self._update_selected_tags()

    def _on_selection_changed(self, *args, **kwargs):
        """
        Function that is called each time the user changes scene selection
        """

        sel = cmds.ls(sl=True)
        if len(sel) <= 0:
            self._curr_selection = 'scene'
        else:
            self._curr_selection = sel[0]

        self.update_metadata_node()
        self._update_selected_tags()

    def _update_types(self):

        tagger_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solstice_tagger.json')
        if not os.path.isfile(tagger_file):
            QMessageBox.warning(self, "Tagger info file does not exists!", "Problem with tagger info file! Please contact TD!")
            return

        self._type_grid.clear()
        self._selection_grid.clear()

        categories = utils.read_json(tagger_file)['types']
        for cat in categories:
            tag_widget = TaggerWidget(
                type_title_name=cat['name'],
                type_name=cat['type'],
                type_category='types',
                type_image=cat['image']
            )
            tag_widget.btn.toggled.connect(partial(self.update_tag_data_info, tag_widget.get_category(), tag_widget.get_name()))
            self._type_grid.add_widget_first_empty_cell(tag_widget)

        selections = utils.read_json(tagger_file)['selections']
        for sel in selections:
            tag_widget = TaggerWidget(
                    type_title_name=sel['name'],
                    type_name=sel['type'],
                    type_category='selections',
                    type_image=sel['image']
                )
            tag_widget.btn.toggled.connect(partial(self.update_tag_data_info, tag_widget.get_category(), tag_widget.get_name()))
            self._selection_grid.add_widget_first_empty_cell(tag_widget)

    def set_tags_state(self, state=False):
        """
        Disables/Enables all check buttons for all tag properties
        :param state: bool
        """

        for i in range(self._type_grid.columnCount()):
            for j in range(self._type_grid.rowCount()):
                container_w = self._type_grid.cellWidget(j, i)
                if container_w is not None:
                    tag_w = container_w.containedWidget
                    tag_w.btn.setChecked(state)
        for i in range(self._selection_grid.columnCount()):
            for j in range(self._selection_grid.rowCount()):
                container_w = self._selection_grid.cellWidget(j, i)
                if container_w is not None:
                    tag_w = container_w.containedWidget
                    tag_w.btn.setChecked(state)

    def _update_selected_tags(self):

        tag_data_node = self.get_tag_data_node_from_curr_sel()

        print(tag_data_node)

        self.set_tags_state(False)

        if tag_data_node is not None and cmds.attributeQuery('types', node=tag_data_node, exists=True):
            types = cmds.getAttr(tag_data_node + '.types')
            selections = cmds.getAttr(tag_data_node + '.selections')
            description = cmds.getAttr(tag_data_node + '.description')
            if types is not None and types != '':
                types = types.split()
                for t in types:
                    for i in range(self._type_grid.columnCount()):
                        for j in range(self._type_grid.rowCount()):
                            container_w = self._type_grid.cellWidget(j, i)
                            if container_w is not None:
                                tag_w = container_w.containedWidget
                                tag_name = tag_w.get_name()
                                if tag_name == t:
                                    tag_w.btn.setChecked(True)
            if selections is not None and selections != '':
                selections = selections.split()
                for s in selections:
                    for i in range(self._selection_grid.columnCount()):
                        for j in range(self._selection_grid.rowCount()):
                            container_w = self._selection_grid.cellWidget(j, i)
                            if container_w is not None:
                                tag_w = container_w.containedWidget
                                tag_name = tag_w.get_name()
                                if tag_name == s:
                                    tag_w.btn.setChecked(True)

            if description is not None and description != '':
                self._description_text.setText(description)

        self._update_current_info()

    def _update_metadata_node_for_curr_selection(self):

        curr_selection = self._curr_selection

        if not self.curr_sel_has_metadata_node():
            if self._curr_selection != 'scene':
                new_tag_data_node = cmds.createNode('network', name='tag_data')
                cmds.addAttr(new_tag_data_node, ln='node', at='message')
                if not cmds.attributeQuery('tag_data', node=curr_selection, exists=True):
                    cmds.addAttr(curr_selection, ln='tag_data', at='message')
                cmds.connectAttr(new_tag_data_node+'.node', curr_selection+'.tag_data')
                cmds.select(curr_selection)
                self._update_metadata_node_for_curr_selection()
            else:
                new_tag_data_node = cmds.createNode('network', name='tag_data_scene')
                cmds.select(clear=True)
        else:
            tag_data_node = self.get_tag_data_node_from_curr_sel()
            for attr in self.tag_attributes:
                if not cmds.attributeQuery(attr, node=tag_data_node, exists=True):
                    cmds.addAttr(tag_data_node, ln=attr, dt='string')

        if curr_selection == 'scene':
            cmds.select(clear=True)
        else:
            cmds.select(curr_selection)

        self._on_selection_changed()

    def _update_current_info(self):
        self._curr_selection_lbl.setText(self._curr_selection)

        if not self.curr_sel_has_metadata_node():
            self._curr_info_lbl.setText('Selected object "{0}" has not valid metadata info!'.format(self._curr_selection))
            self._curr_info_image.setPixmap(self._error_pixmap)
            return

        if not self.check_if_metadata_node_has_valid_info():
            self._curr_info_lbl.setText('Object "{0}" has not valid Tag Data information!'.format(self._curr_selection))
            self._curr_info_image.setPixmap(self._warning_pixmap)
            return

        self._curr_info_lbl.setText('Object "{0}" valid Tag Data information!'.format(self._curr_selection))
        self._curr_info_image.setPixmap(self._ok_pixmap)

    def update_metadata_node(self):
        """
        If a valid Maya object is selected, tagger tabs is show or hide otherwise
        """

        if self.curr_sel_has_metadata_node():
            self._tagger_widgets.setCurrentWidget(self._tagger_tabs)
        else:
            self._tagger_widgets.setCurrentWidget(self._new_tagger_node_widget)
            self._new_tagger_node_btn.setText('Create Tag Data node for "{0}"?'.format(self._curr_selection))

    def curr_sel_has_metadata_node(self):
        """
        Returns True if the current selection has a valid tag data node associated to it or False otherwise
        :return: bool
        """

        if self._curr_selection == 'scene':
            if cmds.objExists('tag_data_scene'):
                return True
        else:
            if not cmds.objExists(self._curr_selection):
                return False
            if cmds.attributeQuery('tag_data', node=self._curr_selection, exists=True):
                if cmds.listConnections(self._curr_selection+'.tag_data') is not None:
                    return True

        return False

    def get_tag_data_node_from_curr_sel(self):
        if self._curr_selection == 'scene':
            try:
                tag_data_node = cmds.ls('tag_data_scene')[0]
            except Exception:
                return None
        else:
            try:
                tag_data_node = cmds.listConnections(self._curr_selection + '.tag_data')[0]
            except Exception:
                return None

        return tag_data_node

    def check_if_metadata_node_has_valid_info(self):

        tag_data_node = self.get_tag_data_node_from_curr_sel()

        if tag_data_node is not None and cmds.attributeQuery('types', node=tag_data_node, exists=True):
            types = cmds.getAttr(tag_data_node+'.types')
            selections = cmds.getAttr(tag_data_node+'.selections')
            if types is not None and types != '':
                return True
            if selections is not None and selections != '':
                return True
        return False

    def update_tag_data_info(self, category, tag_name, tag_value):

        tag_data_node = self.get_tag_data_node_from_curr_sel()
        if tag_data_node is None:
            return

        if tag_value:
            if category == 'types':
                types = cmds.getAttr(tag_data_node+'.types')
                if types is None or types == '':
                    types = tag_name
                else:
                    types_split = types.split()
                    if tag_name in types_split:
                        return
                    types_split.append(tag_name)
                    types = ''.join(str(e)+' ' for e in types_split)
                cmds.setAttr(tag_data_node+'.types', types, type='string')
            elif category == 'selections':
                selections = cmds.getAttr(tag_data_node+'.selections')
                if selections is None or selections == '':
                    selections = tag_name
                else:
                    selections_split = selections.split()
                    if tag_name in selections_split:
                        return
                    selections_split.append(tag_name)
                    selections = ''.join(str(e) + ' ' for e in selections_split)
                cmds.setAttr(tag_data_node+'.selections', selections, type='string')
            elif category == 'description':
                cmds.setAttr(tag_data_node+'.description', self._description_text.toPlainText(), type='string')
        else:
            if category == 'types':
                types = cmds.getAttr(tag_data_node+'.types')
                if types is None or types == '':
                    return
                types_split = types.split()
                if tag_name in types_split:
                    types_split.remove(tag_name)
                else:
                    return
                types = ''.join(str(e) + ' ' for e in types_split)
                cmds.setAttr(tag_data_node + '.types', types, type='string')
            elif category == 'selections':
                selections = cmds.getAttr(tag_data_node+'.selections')
                if selections is None or selections == '':
                    return
                selections_split = selections.split()
                if tag_name in selections_split:
                    selections_split.remove(tag_name)
                else:
                    return
                selections = ''.join(str(e) + ' ' for e in selections_split)
                cmds.setAttr(tag_data_node + '.selections', selections, type='string')
            elif category == 'description':
                cmds.setAttr(tag_data_node+'.description', self._description_text.toPlainText(), type='string')

        self._update_current_info()


def run():
    reload(utils)
    reload(solstice_grid)
    reload(solstice_buttons)
    reload(solstice_label)
    SolsticeTagger.run()
