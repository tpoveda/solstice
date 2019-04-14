#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tagger.py
# by Tomas Poveda
# Tool used to manage metadata for each asset in Solstice Short Film
# ______________________________________________________________________
# ==================================================================="""

import os
from functools import partial

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *

import pipeline as sp
from pipeline.gui import windowds, grid, label
from pipeline.utils import pythonutils as utils
from pipeline.resources import resource

if sp.is_maya():
    import maya.cmds as cmds
    import maya.OpenMaya as OpenMaya


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


class TaggerEditor(QWidget, object):

    dataUpdated = Signal()

    def __init__(self, parent=None):
        super(TaggerEditor, self).__init__(parent=parent)

    def initialize(self):
        pass

    def update_tag_buttons_state(self, sel=None):
        pass

    def update_data(self, data, *args, **kwargs):
        pass


class NameEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(NameEditor, self).__init__(parent=parent)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        name_lbl = QLabel('Name: ')
        self._name_line = QLineEdit()
        self.main_layout.addWidget(name_lbl)
        self.main_layout.addWidget(self._name_line)

        self._name_line.textChanged.connect(partial(self.update_data, None))

    def update_tag_buttons_state(self, sel):
        """
        Updates the selection tag attribute of the tag data node
        :param name: str, name of the selection tag to add/remove
        """

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('name', node=tag_data_node, exists=True)
        if attr_exists:
            name = cmds.getAttr(tag_data_node + '.name')
            if name is not None and name != '':
                self._name_line.setText(name)

    def update_data(self, data, *args, **kwargs):
        """
        Update the data in the tag data node that is managed by this editor
        :param data: variant
        """

        sel = kwargs.pop('sel', None)

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('name', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='name', dt='string')

        cmds.setAttr(tag_data_node+'.name', lock=False)
        cmds.setAttr(tag_data_node + '.name', self._name_line.text(), type='string')
        cmds.setAttr(tag_data_node + '.name', lock=True)
        self.dataUpdated.emit()


class TypeEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(TypeEditor, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._type_grid = grid.GridWidget()
        self._type_grid.setShowGrid(False)
        self._type_grid.setColumnCount(4)
        self._type_grid.horizontalHeader().hide()
        self._type_grid.verticalHeader().hide()
        self._type_grid.resizeRowsToContents()
        self._type_grid.resizeColumnsToContents()
        self.main_layout.addWidget(self._type_grid)

    def initialize(self):
        tagger_file = SolsticeTagger.get_tagger_file()
        self._type_grid.clear()

        categories = utils.read_json(tagger_file)['types']
        for cat in categories:
            tag_widget = TaggerWidget(
                type_title_name=cat['name'],
                type_name=cat['type'],
                type_category='types',
                type_image=cat['image']
            )
            tag_widget.btn.toggled.connect(partial(self.update_data, tag_widget.get_name()))
            self._type_grid.add_widget_first_empty_cell(tag_widget)

    def update_tag_buttons_state(self, sel=None):
        """
        Updates the type tag attribute of the tag data node
        :param name: str, name of the type tag to add/remove
        """

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        self.set_tag_widgets_state(False)

        attr_exists = cmds.attributeQuery('types', node=tag_data_node, exists=True)
        if attr_exists:
            types = cmds.getAttr(tag_data_node + '.types')
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
                                    tag_w.btn.blockSignals(True)
                                    tag_w.btn.setChecked(True)
                                    tag_w.btn.blockSignals(False)

    def update_data(self, data, *args, **kwargs):
        """
        Update the data in the tag data node that is managed by this editor
        :param data: variant
        """

        sel = kwargs.pop('sel', None)

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('types', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='types', dt='string')

        types = cmds.getAttr(tag_data_node + '.types')
        if args[0]:
            if types is None or types == '':
                types = data
            else:
                types_split = types.split()
                if data in types_split:
                    return
                types_split.append(data)
                types = ''.join(str(e) + ' ' for e in types_split)
            cmds.setAttr(tag_data_node + '.types', lock=False)
            cmds.setAttr(tag_data_node+'.types', types, type='string')
            cmds.setAttr(tag_data_node + '.types', lock=True)
        else:
            if types is None or types == '':
                return
            types_split = types.split()
            if data in types_split:
                types_split.remove(data)
            else:
                return
            types = ''.join(str(e) + ' ' for e in types_split)

            cmds.setAttr(tag_data_node + '.types', lock=False)
            cmds.setAttr(tag_data_node + '.types', types, type='string')
            cmds.setAttr(tag_data_node + '.types', lock=True)

        self.dataUpdated.emit()

    def set_tag_widgets_state(self, state=False):
        """
        Disables/Enables all tag buttons on the grid layout
        :param state: bool
        """

        for i in range(self._type_grid.columnCount()):
            for j in range(self._type_grid.rowCount()):
                container_w = self._type_grid.cellWidget(j, i)
                if container_w is not None:
                    tag_w = container_w.containedWidget
                    tag_w.btn.blockSignals(True)
                    tag_w.btn.setChecked(state)
                    tag_w.btn.blockSignals(False)


class SelectionEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(SelectionEditor, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._selection_grid = grid.GridWidget()
        self._selection_grid.setShowGrid(False)
        self._selection_grid.setColumnCount(4)
        self._selection_grid.horizontalHeader().hide()
        self._selection_grid.verticalHeader().hide()
        self._selection_grid.resizeRowsToContents()
        self._selection_grid.resizeColumnsToContents()
        self.main_layout.addWidget(self._selection_grid)

    def initialize(self):
        tagger_file = SolsticeTagger.get_tagger_file()
        self._selection_grid.clear()

        selections = utils.read_json(tagger_file)['selections']
        for cat in selections:
            tag_widget = TaggerWidget(
                type_title_name=cat['name'],
                type_name=cat['type'],
                type_category='types',
                type_image=cat['image']
            )
            tag_widget.btn.toggled.connect(partial(self.update_data, tag_widget.get_name()))
            self._selection_grid.add_widget_first_empty_cell(tag_widget)

    def update_tag_buttons_state(self, sel=None):
        """
        Updates the selection tag attribute of the tag data node
        :param name: str, name of the selection tag to add/remove
        """

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        self.set_tag_widgets_state(False)

        attr_exists = cmds.attributeQuery('selections', node=tag_data_node, exists=True)
        if attr_exists:
            selections = cmds.getAttr(tag_data_node + '.selections')
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
                                    tag_w.btn.blockSignals(True)
                                    tag_w.btn.setChecked(True)
                                    tag_w.btn.blockSignals(False)

    def update_data(self, data, *args, **kwargs):
        """
        Update the data in the tag data node that is managed by this editor
        :param data: variant
        """

        sel = kwargs.pop('sel', None)

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('selections', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='selections', dt='string')

        selections = cmds.getAttr(tag_data_node + '.selections')
        if args[0]:
            if selections is None or selections == '':
                selections = data
            else:
                selections_split = selections.split()
                if data in selections_split:
                    return
                selections_split.append(data)
                selections = ''.join(str(e) + ' ' for e in selections_split)
            cmds.setAttr(tag_data_node + '.selections', lock=False)
            cmds.setAttr(tag_data_node + '.selections', selections, type='string')
            cmds.setAttr(tag_data_node + '.selections', lock=True)
        else:
            if selections is None or selections == '':
                return
            selections_split = selections.split()
            if data in selections_split:
                selections_split.remove(data)
            else:
                return
            selections = ''.join(str(e) + ' ' for e in selections_split)

            cmds.setAttr(tag_data_node + '.selections', lock=False)
            cmds.setAttr(tag_data_node + '.selections', selections, type='string')
            cmds.setAttr(tag_data_node + '.selections', lock=True)

        self.dataUpdated.emit()

    def set_tag_widgets_state(self, state=False):
        """
        Disables/Enables all tag buttons on the grid layout
        :param state: bool
        """

        for i in range(self._selection_grid.columnCount()):
            for j in range(self._selection_grid.rowCount()):
                container_w = self._selection_grid.cellWidget(j, i)
                if container_w is not None:
                    tag_w = container_w.containedWidget
                    tag_w.btn.blockSignals(True)
                    tag_w.btn.setChecked(state)
                    tag_w.btn.blockSignals(False)


class HighProxyEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(HighProxyEditor, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        low_layout = QHBoxLayout()
        low_lbl = QLabel('Proxy: ')
        self.low_line = label.DragDropLine()
        self.low_line.setReadOnly(True)
        low_layout.addWidget(low_lbl)
        low_layout.addWidget(self.low_line)
        self.main_layout.addLayout(low_layout)
        high_layout = QHBoxLayout()
        high_lbl = QLabel('High: ')
        self.high_line = label.DragDropLine()
        self.high_line.setReadOnly(True)
        high_layout.addWidget(high_lbl)
        high_layout.addWidget(self.high_line)
        self.main_layout.addLayout(high_layout)

        self.check_btn = QPushButton('Update Proxy/Hires groups')
        self.main_layout.addWidget(self.check_btn)

        self.check_btn.clicked.connect(partial(self.update_data, None))

        # self.low_line.textChanged.connect(partial(self.update_data, None))
        # self.high_line.textChanged.connect(partial(self.update_data, None))

    def update_tag_buttons_state(self, sel=None):
        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None  or not cmds.objExists(tag_data_node):
            return

        attr_exists = cmds.attributeQuery('proxy', node=tag_data_node, exists=True)
        if attr_exists:
            proxy_group = cmds.listConnections(tag_data_node + '.proxy')
            if proxy_group:
                proxy_group = proxy_group[0]
            if proxy_group is not None and cmds.objExists(proxy_group):
                self.low_line.setText(proxy_group)

        attr_exists = cmds.attributeQuery('hires', node=tag_data_node, exists=True)
        if attr_exists:
            hires_group = cmds.listConnections(tag_data_node + '.hires')
            if hires_group:
                hires_group = hires_group[0]
            if hires_group is not None and cmds.objExists(hires_group):
                self.high_line.setText(hires_group)

    def update_data(self, data, *args, **kwargs):

        sel = kwargs.pop('sel', None)

        self.update_proxy_group()
        self.update_hires_group()
        self.update_tag_buttons_state(sel)

    @staticmethod
    def update_proxy_group(tag_data=None):

        if not tag_data:
            tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel()
            if tag_data_node is None or not cmds.objExists(tag_data_node):
                return
        else:
            if not cmds.objExists(tag_data):
                sp.logger.error('Tag Data {} does not exists in current scene!'.format(tag_data))
                return False
            tag_data_node = tag_data

        attr_exists = cmds.attributeQuery('proxy', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='proxy', at='message')

        sel_name = cmds.ls(SolsticeTagger.current_selection, long=True)
        if len(sel_name) > 1:
            sp.logger.error('Multiple assets with same name: {}'.format(SolsticeTagger.current_selection))
            return False
        sel_name = sel_name[0]

        # Check proxy group connection
        proxy_path = None
        if cmds.objExists(sel_name):
            name = sel_name.split('|')[-1]
            proxy_name = '{}_proxy_grp'.format(name)
            children = cmds.listRelatives(sel_name, allDescendents=True, type='transform', fullPath=True)
            if not children:
                sp.logger.error('Proxy Group not found!')
                return False
            for obj in children:
                base_name = obj.split('|')[-1]
                if base_name == proxy_name:
                    if proxy_path is None:
                        proxy_path = obj
                    else:
                        sp.logger.error('Multiple proxy groups in the asset. Asset only can have one proxy group: {}'.format(proxy_name))
                        return False
        if proxy_path is None or not cmds.objExists(proxy_path):
            sp.logger.error('Proxy Group not found!')
            return False
        try:
            cmds.setAttr(tag_data_node + '.proxy', lock=False)
            cmds.connectAttr(proxy_path + '.message', tag_data_node + '.proxy', force=True)
        except Exception:
            pass

        cmds.setAttr(tag_data_node + '.proxy', lock=True)

        return True

    @staticmethod
    def update_hires_group(tag_data=None):
        if not tag_data:
            tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel()
            if tag_data_node is None or not cmds.objExists(tag_data_node):
                return
        else:
            if not cmds.objExists(tag_data):
                sp.logger.error('Tag Data {} does not exists in current scene!'.format(tag_data))
                return False
            tag_data_node = tag_data

        attr_exists = cmds.attributeQuery('hires', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='hires', at='message')

        sel_name = cmds.ls(SolsticeTagger.current_selection, long=True)
        if len(sel_name) > 1:
            sp.logger.error('Multiple assets with same name: {}'.format(SolsticeTagger.current_selection))
            return False
        sel_name = sel_name[0]

        # Check hires group connection
        hires_path = None
        if cmds.objExists(sel_name):
            name = sel_name.split('|')[-1]
            hires_name = '{}_hires_grp'.format(name)
            children = cmds.listRelatives(sel_name, allDescendents=True, type='transform', fullPath=True)
            if not children:
                sp.logger.error('Hires Group not found!')
                return False
            for obj in children:
                base_name = obj.split('|')[-1]
                if base_name == hires_name:
                    if hires_path is None:
                        hires_path = obj
                    else:
                        sp.logger.error(
                            'Multiple hires groups in the asset. Asset only can have one hires group: {}'.format(
                                hires_name))
                        return False
        if hires_path is None or not cmds.objExists(hires_path):
            sp.logger.error('Hires Group not found!')
            return False
        try:
            cmds.setAttr(tag_data_node + '.hires', lock=False)
            cmds.connectAttr(hires_path + '.message', tag_data_node + '.hires', force=True)
        except Exception:
            pass

        cmds.setAttr(tag_data_node + '.hires', lock=True)

        return True


class DescriptionEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(DescriptionEditor, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._description_text = QTextEdit()
        self.main_layout.addWidget(self._description_text)

        self._description_text.textChanged.connect(partial(self.update_data, None))

    def update_tag_buttons_state(self, sel=None):
        """
        Updates the selection tag attribute of the tag data node
        :param name: str, name of the selection tag to add/remove
        """

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('description', node=tag_data_node, exists=True)
        if attr_exists:
            description = cmds.getAttr(tag_data_node + '.description')
            if description is not None and description != '':
                self._description_text.setText(description)

    def update_data(self, data, *args, **kwargs):
        """
        Update the data in the tag data node that is managed by this editor
        :param data: variant
        """

        sel = kwargs.pop('sel', None)

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('description', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='description', dt='string')

        cmds.setAttr(tag_data_node + '.description', lock=False)
        cmds.setAttr(tag_data_node + '.description', self._description_text.toPlainText(), type='string')
        cmds.setAttr(tag_data_node + '.description', lock=True)
        self.dataUpdated.emit()


class ShadersEditor(TaggerEditor, object):
    def __init__(self, parent=None):
        super(ShadersEditor, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self._update_shaders_btn = QPushButton('Update Shaders')
        self.main_layout.addWidget(self._update_shaders_btn)

        self._update_shaders_btn.clicked.connect(partial(self.update_data, None))

    def update_tag_buttons_state(self, sel=None):
        """
        Updates the selection tag attribute of the tag data node
        :param name: str, name of the selection tag to add/remove
        """

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('shaders', node=tag_data_node, exists=True)
        if attr_exists:
            pass
            # description = cmds.getAttr(tag_data_node + '.description')
            # if description is not None and description != '':
            #     self._description_text.setText(description)

    def update_data(self, data, *args, **kwargs):
        """
        Update the data in the tag data node that is managed by this editor
        :param data: variant
        """

        sel = kwargs.pop('sel', None)

        tag_data_node = SolsticeTagger.get_tag_data_node_from_curr_sel(sel)
        if tag_data_node is None:
            return

        attr_exists = cmds.attributeQuery('shaders', node=tag_data_node, exists=True)
        if not attr_exists:
            cmds.addAttr(tag_data_node, ln='shaders', dt='string')

        asset_groups = cmds.ls('*_grp', type='transform')
        if len(asset_groups <= 0):
            return

        # all_shading_groups = list()
        # json_data = dict()
        # for grp in asset_groups:
        #     json_data[grp] = dict()
        #     children = cmds.listRelatives(grp, type='transform', allDescendents=True, fullPath=True)
        #     for child in children:
        #         child_shapes = cmds.listRelatives(child, shapes=True, fullPath=True)
        #         for shape in child_shapes:
        #             json_data[grp][shape] = dict()
        #             shading_groups = cmds.listConnections(shape, type='shadingEngine')
        #             for shading_grp in shading_groups:
        #                 shading_grp_mat = cmds.ls(cmds.listConnections(shading_grp), materials=True)
        #                 json_data[grp][shape][shading_grp] = shading_grp_mat



        # cmds.setAttr(tag_data_node + '.description', lock=False)
        # cmds.setAttr(tag_data_node + '.description', self._description_text.toPlainText(), type='string')
        # cmds.setAttr(tag_data_node + '.description', lock=True)
        self.dataUpdated.emit()


class SolsticeTagger(windowds.Window, object):

    name = 'SolsticeTagger'
    title = 'Solstice Tools - Tagger'
    version = '1.2'

    tagDataCreated = Signal()

    current_selection = 'scene'
    tag_attributes = ['types', 'selections', 'description']

    def __init__(self):

        super(SolsticeTagger, self).__init__()
        self.add_callback(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed, self))

    def custom_ui(self):
        super(SolsticeTagger, self).custom_ui()

        self.set_logo('solstice_tagger_logo')

        self.resize(300, 300)

        self._error_pixmap = resource.pixmap('error', category='icons').scaled(QSize(24, 24))
        self._warning_pixmap = resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
        self._ok_pixmap = resource.pixmap('ok', category='icons').scaled(QSize(24, 24))

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
        self._curr_selection_lbl = QLabel(self.current_selection)
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

        self._tagger_widgets = QStackedWidget(self)
        tagger_editor_layout.addWidget(self._tagger_widgets)

        self._new_tagger_node_widget = QWidget()
        new_tagger_node_layout = QVBoxLayout()
        new_tagger_node_layout.setContentsMargins(35, 5, 35, 5)
        new_tagger_node_layout.setSpacing(5)
        self._new_tagger_node_widget.setLayout(new_tagger_node_layout)
        self._new_tagger_node_btn = QPushButton('Create Tag Data node for "{0}"?'.format(self.current_selection))
        new_tagger_node_layout.addWidget(self._new_tagger_node_btn)
        self._tagger_widgets.addWidget(self._new_tagger_node_widget)

        # ======================================================================================

        self._tagger_tabs = QTabWidget()
        self._tagger_widgets.addWidget(self._tagger_tabs)

        self.name_editor = NameEditor()
        self.type_editor = TypeEditor()
        self.selection_editor = SelectionEditor()
        self.high_proxy_editor = HighProxyEditor()
        self.description_editor = DescriptionEditor()
        self.shaders_editor = ShadersEditor()

        self._tagger_tabs.addTab(self.name_editor, 'Name')
        self._tagger_tabs.addTab(self.type_editor, 'Type')
        self._tagger_tabs.addTab(self.selection_editor, 'Selections')
        self._tagger_tabs.addTab(self.high_proxy_editor, 'Proxy/High')
        self._tagger_tabs.addTab(self.description_editor, 'Description')
        self._tagger_tabs.addTab(self.shaders_editor, 'Shaders')

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        self.main_layout.addLayout(bottom_layout)
        select_tag_data_btn = QPushButton('Select Tag Data')
        remove_tag_data_btn = QPushButton('Remove Tag Data')
        export_tag_data_btn = QPushButton('Export Tag Data')
        export_tag_data_btn.setEnabled(False)
        import_tag_data_btn = QPushButton('Import Tag Data')
        import_tag_data_btn.setEnabled(False)
        bottom_layout.addWidget(select_tag_data_btn)
        bottom_layout.addWidget(remove_tag_data_btn)
        bottom_layout.addWidget(export_tag_data_btn)
        bottom_layout.addWidget(import_tag_data_btn)

        # ================================================================================

        self._new_tagger_node_btn.clicked.connect(self._create_new_tag_data_node_for_current_selection)
        select_tag_data_btn.clicked.connect(self.select_tag_data_node)
        remove_tag_data_btn.clicked.connect(self.remove_tag_data_node)

        # ================================================================================

        for i in range(self._tagger_tabs.count()):
            self._tagger_tabs.widget(i).dataUpdated.connect(self._update_current_info)
            self._tagger_tabs.widget(i).initialize()

        self._on_selection_changed()

    @staticmethod
    def get_tagger_file():
        """
        Returns file path where solstice_tagger.json is stored
        :return: str
        """

        tagger_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'solstice_tagger.json')
        if not os.path.isfile(tagger_file):
            QMessageBox.warning(None, "Tagger info file does not exists!", "Problem with tagger info file! Please contact TD!")
            return None

        return tagger_file

    @classmethod
    def get_tag_data_node_from_curr_sel(cls, new_selection=None):
        """
        Returns the tag data node associated to the current selected Maya object
        :return: variant, None || str
        """

        if new_selection:
            if cmds.objExists(new_selection):
                cls.current_selection = new_selection

        if cls.current_selection == 'scene':
            try:
                tag_data_node = cmds.ls('tag_data_scene')[0]
            except Exception:
                return None
        else:
            try:
                tag_data_node = cmds.listConnections(cls.current_selection + '.tag_data')[0]
            except Exception:
                return None

        return tag_data_node

    @classmethod
    def select_tag_data_node(cls):
        """
        Selects the tag data node associated to the current selected Maya object
        """

        tag_data_node = cls.get_tag_data_node_from_curr_sel()
        if tag_data_node is None:
            return
        cmds.select(tag_data_node)

    @classmethod
    def curr_sel_has_metadata_node(cls):
        """
        Returns True if the current selection has a valid tag data node associated to it or False otherwise
        :return: bool
        """

        if cls.current_selection == 'scene':
            if cmds.objExists('tag_data_scene'):
                return True
        else:
            if not cmds.objExists(cls.current_selection):
                return False
            if cmds.attributeQuery('tag_data', node=cls.current_selection, exists=True):
                if cmds.listConnections(cls.current_selection+'.tag_data') is not None:
                    return True

        return False

    @classmethod
    def check_if_metadata_node_has_valid_info(cls):

        tag_data_node = cls.get_tag_data_node_from_curr_sel()
        user_defined_attrs = cmds.listAttr(tag_data_node, userDefined=True)
        if user_defined_attrs and len(user_defined_attrs) > 0:
            return True

        return False

    def remove_tag_data_node(self):
        """
        Removes the tag data node associated to the current selected Maya object
        """

        tag_data_node = self.get_tag_data_node_from_curr_sel()
        if tag_data_node is None:
            return
        cmds.delete(tag_data_node)
        self._update_ui()
        self._update_current_info()
        for i in range(self._tagger_tabs.count()):
            self._tagger_tabs.widget(i).update_tag_buttons_state()
            self._tagger_tabs.widget(i).update_data(None)

    def _on_selection_changed(self, *args, **kwargs):
        """
        Function that is called each time the user changes scene selection
        """

        sel = cmds.ls(sl=True)

        if len(sel) <= 0:
            SolsticeTagger.current_selection = 'scene'
            sel = None
        else:
            SolsticeTagger.current_selection = sel[0]
            sel = sel[0]

        self._update_current_info()
        self._update_ui()
        for i in range(self._tagger_tabs.count()):
            self._tagger_tabs.widget(i).update_tag_buttons_state(sel)

    def _update_ui(self):
        """
        If a valid Maya object is selected, tagger tabs is show or hide otherwise
        """

        if self.curr_sel_has_metadata_node():
            self._tagger_widgets.setCurrentWidget(self._tagger_tabs)
        else:
            self._tagger_widgets.setCurrentWidget(self._new_tagger_node_widget)
            self._new_tagger_node_btn.setText('Create Tag Data node for "{0}"?'.format(self.current_selection))

    def _update_current_info(self):
        """
        Updates the widget that is showed in the SolsticeTagger UI
        :return:
        """
        self._curr_selection_lbl.setText(self.current_selection)

        if not self.curr_sel_has_metadata_node():
            self._curr_info_lbl.setText('Selected object "{0}" has not valid metadata info!'.format(self.current_selection))
            self._curr_info_image.setPixmap(self._error_pixmap)
            return

        if not self.check_if_metadata_node_has_valid_info():
            self._curr_info_lbl.setText('Object "{0}" has not valid Tag Data information!'.format(self.current_selection))
            self._curr_info_image.setPixmap(self._warning_pixmap)
            return

        self._curr_info_lbl.setText('Object "{0}" valid Tag Data information!'.format(self.current_selection))
        self._curr_info_image.setPixmap(self._ok_pixmap)

    def _create_new_tag_data_node_for_current_selection(self):
        self.create_new_tag_data_node_for_current_selection()
        self.tagDataCreated.emit()
        self._on_selection_changed()

    @classmethod
    def create_new_tag_data_node_for_current_selection(cls, asset_type=None):

        if not cls.current_selection or cls.current_selection == 'scene' or not cmds.objExists(cls.current_selection):
            cls.current_selection = cmds.ls(sl=True)
            if cls.current_selection:
                cls.current_selection = cls.current_selection[0]

        curr_selection = cls.current_selection

        if not cls.curr_sel_has_metadata_node():
            if cls.current_selection != 'scene':
                new_tag_data_node = cmds.createNode('network', name='tag_data')
                cmds.addAttr(new_tag_data_node, ln='tag_type', dt='string')
                cmds.setAttr(new_tag_data_node + '.tag_type', 'SOLSTICE_TAG', type='string')
                cmds.setAttr(new_tag_data_node + '.tag_type', keyable=False)
                cmds.setAttr(new_tag_data_node + '.tag_type', channelBox=False)
                cmds.setAttr(new_tag_data_node + '.tag_type', lock=True)
                cmds.addAttr(new_tag_data_node, ln='node', at='message')
                if not cmds.attributeQuery('tag_data', node=curr_selection, exists=True):
                    cmds.addAttr(curr_selection, ln='tag_data', at='message')
                cmds.setAttr(curr_selection + '.tag_data', lock=False)
                cmds.setAttr(new_tag_data_node + '.node', lock=False)
                cmds.connectAttr(new_tag_data_node+'.node', curr_selection+'.tag_data')
                cmds.setAttr(curr_selection + '.tag_data', lock=True)
                cmds.setAttr(new_tag_data_node + '.node', lock=True)
                cmds.select(curr_selection)

                if asset_type is not None and new_tag_data_node:
                    attr_exists = cmds.attributeQuery('types', node=new_tag_data_node, exists=True)
                    if not attr_exists:
                        cmds.addAttr(new_tag_data_node, ln='types', dt='string')
                    if asset_type == 'Props' or asset_type == 'props':
                            cmds.setAttr(new_tag_data_node + '.types', 'prop', type='string')
                    elif asset_type == 'Background Elements' or asset_type == 'background elements':
                            cmds.setAttr(new_tag_data_node + '.types', 'background_element', type='string')
                    elif asset_type == 'Character' or asset_type == 'character':
                            cmds.setAttr(new_tag_data_node + '.types', 'character', type='string')
                    elif asset_type == 'Light Rig' or asset_type == 'light rig':
                            cmds.setAttr(new_tag_data_node + '.types', 'light_rig', type='string')
                    cmds.setAttr(new_tag_data_node + '.types', lock=True)

            else:
                new_tag_data_node = cmds.createNode('network', name='tag_data_scene')
                cmds.select(clear=True)

        if curr_selection == 'scene':
            cmds.select(clear=True)
        else:
            cmds.select(curr_selection)


def run():
    win = SolsticeTagger().show()
