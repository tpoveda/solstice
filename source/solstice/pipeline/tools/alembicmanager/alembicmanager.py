#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to export/import Alembic (.abc) files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import json
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.gui import window, splitters
from solstice.pipeline.resources import resource
from solstice.pipeline.utils import browserutils, alembic, pythonutils, artellautils

from solstice.pipeline.tools.tagger import tagger

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.utils import mayautils


ALEMBIC_GROUP_SUFFIX = '_ABCGroup'


class AlembicGroup(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicGroup, self).__init__(parent=parent)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        group_layout = QGridLayout()
        group_layout.setContentsMargins(2, 2, 2, 2)
        group_layout.setSpacing(2)
        self.main_layout.addLayout(group_layout)

        group_name_lbl = QLabel('Group Name: ')
        self.name_line = QLineEdit()
        group_layout.addWidget(group_name_lbl, 0, 0, 1, 1, Qt.AlignRight)
        group_layout.addWidget(self.name_line, 0, 1)

        self.main_layout.addLayout(splitters.SplitterLayout())

        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(25, 5, 25, 5)
        self.main_layout.addLayout(buttons_layout)

        create_btn = QPushButton('Create')
        buttons_layout.addWidget(create_btn)
        buttons_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Expanding))
        clean_alembic_groups_btn = QPushButton('Clean Alembic Groups')
        self.main_layout.addWidget(clean_alembic_groups_btn)

        create_btn.clicked.connect(partial(lambda: self.create_alembic_group(self.name_line.text())))
        clean_alembic_groups_btn.clicked.connect(self.clean_alembic_groups)

    @staticmethod
    def get_alembic_group_name_from_node_name(node_name):
        """
        Returns an alembic group name from the give node name
        :param node_name: str, long name of a Maya node
        :return: str
        """

        if node_name:
            split_name = node_name.split('|')
            if not split_name or len(split_name) == 1:
                return node_name
            split_name = split_name[1]
            rsplit_name = split_name.rsplit(':', 1)
            if not rsplit_name or len(rsplit_name) == 1:
                return node_name
            rsplit_name = rsplit_name[-1]

            return rsplit_name

        return None

    @staticmethod
    def create_alembic_group(name=None, filter_type='transform'):
        """
        Creates a new alembic group (set)
        :param name: str, name of the alembic group
        :param filter_type:
        :return: str, new alembic group created
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('DCC {} does not supports the creation of Alembic groups!'.format(sys.solstice.dcc.get_name()))
            return None

        import maya.cmds as cmds

        sel = sys.solstice.dcc.selected_nodes(full_path=True)
        if not sel:
            sys.solstice.dcc.confirm_dialog(
                title='Impossible to create Alembic Group',
                message='No nodes selected, please select nodes first and try again!')
            return None

        if not name:
            name = AlembicGroup.get_alembic_group_name_from_node_name(sel[0])

        if not name.endswith(ALEMBIC_GROUP_SUFFIX):
            name += ALEMBIC_GROUP_SUFFIX

        if sys.solstice.dcc.object_exists(name):
            res = sys.solstice.dcc.confirm_dialog(
                title='Alembic Group already exists!',
                message='Do you want to overwrite existing Alembic Group?',
                button=['Yes', 'No'],
                default_button='Yes',
                cancel_button='No',
                dismiss_string='No'
            )
            if res and res == 'Yes':
                sys.solstice.dcc.delete_object(name)

        sys.solstice.logger.debug('Creating Alembic Group with name: {}'.format(name))

        full_sel = sys.solstice.dcc.list_relatives(node=sel, all_hierarchy=True, full_path=True) or []
        main_sel = list()
        for n in full_sel:
            p = sys.solstice.dcc.node_parent(node=n, full_path=True)
            p = p[0] if p else None
            if p and p in full_sel:
                continue
            main_sel.append(n)

        final_sel = None
        if filter_type:
            final_sel = filter(lambda x: sys.solstice.dcc.check_object_type(node=x, node_type=filter_type), main_sel)
        if final_sel is None:
            sys.solstice.dcc.confirm_dialog(
                title='Impossible to create Alembic Group',
                message='No objects found with filter type {}!'.format(filter_type)
            )

        return cmds.sets(sel, n=name)

    # @solstice_maya_utils.maya_undo
    @staticmethod
    def clean_alembic_groups():
        """
        Removes all alembic groups in current scene
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('DCC {} does not supports the creation of Alembic groups!'.format(sys.solstice.dcc.get_name()))
            return None

        import maya.cmds as cmds

        all_sets = cmds.listSets(allSets=True)
        abc_sets = [s for s in all_sets if s.endswith(ALEMBIC_GROUP_SUFFIX)]

        res = sys.solstice.dcc.confirm_dialog(
            title='Removing Alembic Groups!',
            message='Do you want to remove following Alembic Groups?\n' + '\n'.join(abc_sets),
            button=['Yes', 'No'],
            default_button='Yes',
            cancel_button='No',
            dismiss_string='No'
        )
        if res and res == 'Yes':
            cmds.delete(abc_sets)

# ===================================================================================================================

class AlembicExporterNode(object):
    def __init__(self, name, parent=None):

        super(AlembicExporterNode, self).__init__()

        self._name = name
        self._children = []
        self._parent = parent
        self.model = None

        if parent is not None:
            parent.addChild(self)

    def attrs(self):

        classes = self.__class__.__mro__

        kv = {}

        for cls in classes:
            for k, v in cls.__dict__.iteritems():
                if isinstance(v, property):
                    print("Property:", k.rstrip("_"), "\n\tValue:", v.fget(self))
                    kv[k] = v.fget(self)

        return kv

    def typeInfo(self):
        return 'node'

    def addChild(self, child):
        self.model.layoutAboutToBeChanged.emit()
        self._children.append(child)
        child._parent = self
        child.model = self.model
        self.model.layoutChanged.emit()

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self.model.layoutAboutToBeChanged.emit()
        self._children.insert(position, child)
        child._parent = self
        child.model = self.model
        self.model.layoutChanged.emit()

        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        self.model.layoutAboutToBeChanged.emit()
        child = self._children.pop(position)
        child._parent = None
        child.model = None
        self.model.layoutChanged.emit()

        return True

    def name():
        def fget(self): return self._name

        def fset(self, value): self._name = value

        return locals()

    name = property(**name())

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):

        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "|------" + self._name + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += "\n"

        return output

    def __repr__(self):
        return self.log()

    def data(self, column):

        if column is 0:
            long_name = self.name
            try:
                return long_name.split(':')[-1].split('|')[-1]
            except Exception:
                return long_name
        elif column is 1:
            return self.typeInfo()

    def setData(self, column, value):
        if column is 0:
            self.name = value.toPyObject()
        elif column is 1:
            pass

    def resource(self):
        pass


class AlembicExporterGroupNode(AlembicExporterNode, object):
    def __init__(self, name, parent=None):
        super(AlembicExporterGroupNode, self).__init__(name=name, parent=parent)


class AlembicNode(AlembicExporterNode, object):
    def __init__(self, name, parent=None):
        super(AlembicNode, self).__init__(name=name, parent=parent)

    def resource(self):
        path = resource.get('icons', 'alembic_white_icon.png')
        return path


class AlembicExporterModelHires(AlembicExporterNode, object):
    def __init__(self, name, parent=None):
        super(AlembicExporterModelHires, self).__init__(name=name, parent=parent)


class AlembicExporterGroupsModel(QAbstractItemModel, object):

    sortRole = Qt.UserRole
    filterRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        super(AlembicExporterGroupsModel, self).__init__(parent)
        self._root_node = AlembicExporterNode('Root')
        self._root_node.model = self

    def rowCount(self, parent):
        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        return parent_node.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if not node:
            return

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return node.data(index.column())
        elif role == Qt.DecorationRole:
            resource = node.resource()
            return QIcon(QPixmap(resource))

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()
            if role == Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
                return True

        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if section == 0:
                return 'Alembic'
            else:
                return 'Type'

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def parent(self, index):
        node = self.get_node(index)
        parent_node = node.parent()
        if parent_node == self._root_node:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        parent_node = self.get_node(parent)

        child_item = parent_node.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def insertRows(self, pos, rows, parent=QModelIndex()):
        parent_node = self.get_node(parent)
        self.beginInsertRows(parent, pos, pos + rows - 1)
        for row in range(rows):
            child_count = parent_node.childCount()
            child_node = AlembicExporterNode('Untitled'+str(child_count))
            success = parent_node.insertChild(pos, child_node)
        self.endInsertRows()

        return success

    def removeRows(self, pos, rows, parent=QModelIndex()):
        parent_node = self.get_node(parent)
        self.beginRemoveRows(parent, pos, pos + rows - 1)
        for row in range(rows):
            success = parent_node.removeChild(pos)
        self.endRemoveRows()

        return success

    def get_node(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._root_node

    def clean(self):
        for child_index in range(self._root_node.childCount()):
            self._root_node.removeChild(child_index)


class AlembicExporter(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        buttons_layout = QGridLayout()
        self.main_layout.addLayout(buttons_layout)
        export_tag_lbl = QLabel('Alembic Group: ')
        self.alembic_groups_combo = QComboBox()
        self.alembic_groups_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttons_layout.addWidget(export_tag_lbl, 0, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.alembic_groups_combo, 0, 1)

        name_lbl = QLabel('Alembic Name: ')
        self.name_line = QLineEdit()
        buttons_layout.addWidget(name_lbl, 1, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.name_line, 1, 1)

        shot_name_lbl = QLabel('Shot Name: ')
        self.shot_line = QLineEdit()
        buttons_layout.addWidget(shot_name_lbl, 2, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.shot_line, 2, 1)

        frame_range_lbl = QLabel('Frame Range: ')
        self.start = QSpinBox()
        self.start.setRange(-sys.maxint, sys.maxint)
        self.start.setFixedHeight(20)
        self.start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.end = QSpinBox()
        self.end.setRange(-sys.maxint, sys.maxint)
        self.end.setFixedHeight(20)
        self.end.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame_range_widget = QWidget()
        frame_range_layout = QHBoxLayout()
        frame_range_layout.setContentsMargins(2, 2, 2, 2)
        frame_range_layout.setSpacing(2)
        frame_range_widget.setLayout(frame_range_layout)
        for widget in [frame_range_lbl, self.start, self.end]:
            frame_range_layout.addWidget(widget)
        buttons_layout.addWidget(frame_range_lbl, 3, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(frame_range_widget, 3, 1)

        folder_icon = resource.icon('open')
        export_path_layout = QHBoxLayout()
        export_path_layout.setContentsMargins(2, 2, 2, 2)
        export_path_layout.setSpacing(2)
        export_path_widget = QWidget()
        export_path_widget.setLayout(export_path_layout)
        export_path_lbl = QLabel('Export Path: ')
        self.export_path_line = QLineEdit()
        self.export_path_line.setReadOnly(True)
        self.export_path_line.setText(sp.get_solstice_project_path())
        self.export_path_btn = QPushButton()
        self.export_path_btn.setIcon(folder_icon)
        self.export_path_btn.setIconSize(QSize(18, 18))
        self.export_path_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        export_path_layout.addWidget(self.export_path_line)
        export_path_layout.addWidget(self.export_path_btn)
        buttons_layout.addWidget(export_path_lbl, 4, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(export_path_widget, 4, 1)

        self.open_folder_after_export_cbx = QCheckBox('Open Folder After Export?')
        self.open_folder_after_export_cbx.setChecked(True)
        buttons_layout.addWidget(self.open_folder_after_export_cbx, 5, 1)

        self.main_layout.addLayout(splitters.SplitterLayout())

        export_layout = QHBoxLayout()
        self.export_btn = QPushButton('Export')
        self.export_btn.setEnabled(False)
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        export_layout.addWidget(self.export_btn)
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.main_layout.addLayout(export_layout)

        self.export_path_btn.clicked.connect(self._on_set_export_path)
        self.export_btn.clicked.connect(self._on_export)

        self.main_layout.addLayout(splitters.SplitterLayout())

        self._tree_model = AlembicExporterGroupsModel(self)
        self._abc_tree = QTreeView()
        self._abc_tree.setModel(self._tree_model)
        self.main_layout.addWidget(self._abc_tree)

        self.shot_line.textChanged.connect(self._on_update_tree)
        self.name_line.textChanged.connect(self._on_update_tree)
        self.alembic_groups_combo.currentIndexChanged.connect(self._on_update_tree)

    def refresh(self):
        """
        Function that update necessary info of the tool
        """

        self._tree_model.clean()
        self._refresh_alembic_groups()
        self._refresh_frame_ranges()
        self._refresh_shot_name()
        self._refresh_alembic_name()

    def get_selected_alembic_group(self):
        """
        Returns the name of the currently selected set
        :return: str
        """

        alembic_group_name = self.alembic_groups_combo.currentText()
        return alembic_group_name

    def get_alembic_group_nodes(self, abc_grp_name=None, show_error=True):
        """
        Returns a list of the nodes that are in the given alembic group name
        If no name given the name will be retrieved by the Alembic Group ComboBox
        :return:
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('DCC {} does not supports the retrieving of Alembic Group Nodes!'.format(sys.solstice.dcc.get_name()))
            return None

        import maya.cmds as cmds

        if abc_grp_name:
            if not sys.solstice.dcc.object_exists(abc_grp_name):
                raise Exception('ERROR: Invalid Alembic Group: {}'.format(abc_grp_name))
        else:
            abc_grp_name = self.get_selected_alembic_group()

        if not abc_grp_name:
            if show_error:
                sys.solstice.dcc.confirm_dialog(
                    title='Error during Alembic Exportation',
                    message='No Alembic Group selected. Please select an Alembic Group from the list'
                )
            return None

        set_nodes = cmds.sets(abc_grp_name, q=True, no=True)
        if not set_nodes:
            if show_error:
                sys.solstice.dcc.confirm_dialog(
                    title='Error during Alembic Exportation',
                    message='No members inside selected Alembic Group\n Alembic Group: {}'.format(abc_grp_name)
                )
            return None

        if set_nodes:
            set_nodes = sorted(set_nodes)

        return set_nodes

    def export_alembic(self, export_path, object_to_export=None, start_frame=1, end_frame=1):

        if not object_to_export or not sys.solstice.dcc.object_exists(object_to_export):
            object_to_export = sys.solstice.dcc.selected_nodes(False)
            if not object_to_export:
                sys.solstice.logger.warning('Impossible to export Alembic from inexistent object {}'.format(object_to_export))
                return
            object_to_export = object_to_export[0]

        sys.solstice.dcc.select_object(object_to_export)
        AlembicGroup.create_alembic_group()
        self.refresh()

        self.alembic_groups_combo.setCurrentIndex(1)
        self.export_path_line.setText(export_path)
        self.start.setValue(start_frame)
        self.end.setValue(end_frame)
        self._on_export()

        sys.solstice.dcc.new_file()

    def _refresh_alembic_name(self):
        """
        Internal function that updates Alembic name
        """

        if self.name_line.text() != '':
            return

        sel = sys.solstice.dcc.selected_nodes()
        if sel:
            sel = sel[0]
            is_referenced = sys.solstice.dcc.node_is_referenced(sel)
            if is_referenced:
                sel_namespace = sys.solstice.dcc.node_namespace(sel)
                if not sel_namespace or not sel_namespace.startswith(':'):
                    pass
                else:
                    sel_namespace = sel_namespace[1:] + ':'
                    sel = sel.replace(sel_namespace, '')

            self.name_line.setText(sys.solstice.dcc.node_short_name(sel))

    def _refresh_alembic_groups(self):
        """
        Internal function that updates the list of alembic groups
        """

        self.export_btn.setEnabled(False)

        filtered_sets = filter(lambda x: x.endswith(ALEMBIC_GROUP_SUFFIX), sys.solstice.dcc.list_nodes(node_type='objectSet'))
        filtered_sets.insert(0, '')
        self.alembic_groups_combo.blockSignals(True)
        try:
            self.alembic_groups_combo.clear()
            self.alembic_groups_combo.addItems(filtered_sets)
        except Exception:
            pass
        self.alembic_groups_combo.blockSignals(False)

    def _refresh_frame_ranges(self):
        """
        Internal function that updates the frame ranges values
        """

        frame_range = sys.solstice.dcc.get_time_slider_range()
        self.start.setValue(int(frame_range[0]))
        self.end.setValue(int(frame_range[1]))

    def _refresh_shot_name(self):
        """
        Internal function that updates the shot name QLineEdit text
        """

        shot_name = ''
        current_scene = sys.solstice.dcc.scene_name()
        if current_scene:
            current_scene = os.path.basename(current_scene)

        shot_regex = sp.get_solstice_shot_name_regex()
        m = shot_regex.match(current_scene)
        if m:
            shot_name = m.group(1)

        self.shot_line.setText(shot_name)

    def _on_set_export_path(self):
        """
        Internal function that is calledd when the user selects the folder icon
        Allows the user to select a path to export Alembic group contents
        """

        res = sys.solstice.dcc.select_folder_dial(title='Select Alembic Export Folder', start_directory=sp.get_solstice_project_path())
        if not res:
            return

        self.export_path_line.setText(res)

    def _on_update_tree(self, index, show_error=False):
        set_text = self.get_selected_alembic_group()

        self._tree_model.clean()

        # Add selected Alembic Group to the tree root node
        abc_group_node = AlembicExporterGroupNode(name=set_text)
        self._tree_model._root_node.addChild(abc_group_node)

        abc_group_objs = self.get_alembic_group_nodes(set_text, show_error)
        if not abc_group_objs:
            if set_text != '':
                sys.solstice.logger.warning('Selected Alembic Group is empty: {}'.format(set_text))
            return

        exports_dict = dict()

        for obj in abc_group_objs:
            tag_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(obj)
            if tag_node:
                attr_exists = sys.solstice.dcc.attribute_exists(node=tag_node, attribute_name='hires')
                if not attr_exists:
                    hires_objs = sys.solstice.dcc.list_relatives(node=obj, all_hierarchy=True, full_path=True, relative_type='mesh')
                    if not hires_objs:
                        obj_meshes = [obj]
                    else:
                        obj_meshes = hires_objs
                else:
                    hires_grp = sys.solstice.dcc.list_connections(node=tag_node, attribute_name='hires')
                    if hires_grp and sys.solstice.dcc.object_exists(hires_grp[0]):
                        hires_objs = sys.solstice.dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True, relative_type='mesh')
                    else:
                        hires_objs = sys.solstice.dcc.list_relatives(node=obj, all_hierarchy=True, full_path=True, relative_type='mesh')
                    if not hires_objs:
                        obj_meshes = [obj]
                    else:
                        obj_meshes = hires_objs
            else:
                # obj_meshes = [obj]
                obj_meshes = sys.solstice.dcc.list_relatives(node=obj, all_hierarchy=True, full_path=True, relative_type='mesh')

            exports_dict[obj] = list()
            for o in obj_meshes:
                if o not in exports_dict:
                    exports_dict[obj].append(o)

        if not exports_dict:
            sys.solstice.logger.warning('No objects in Alembic Groups to export')
            return

        shot_name = self.shot_line.text()
        shot_regex = sp.get_solstice_shot_name_regex()
        m = shot_regex.match(shot_name)
        if m:
            shot_name = m.group(1)
        else:
            if self.shot_line.text():
                shot_name = 'Undefined'
            else:
                shot_name = ''

        out_folder = self.export_path_line.text()
        if not os.path.exists(out_folder):
            sys.solstice.logger.warning(
                'Output Path does not exists: {}. Select a valid one!'.format(out_folder)
            )
            return

        is_referenced = sys.solstice.dcc.node_is_referenced(set_text)
        if is_referenced:
            set_namespace = sys.solstice.dcc.node_namespace(set_text)
            if not set_namespace or not set_namespace.startswith(':'):
                export_name = set_text
            else:
                set_namespace = set_namespace[1:] + ':'
                export_name = set_text.replace(set_namespace, '')
        else:
            export_name = set_text

        export_name = export_name.replace(ALEMBIC_GROUP_SUFFIX, '')

        abc_name = self.name_line.text()
        if not abc_name:
            abc_name = export_name

        if shot_name:
            anim_path = '{}_{}'.format(shot_name, abc_name+'.abc')
            filename = os.path.normpath(os.path.join(out_folder, shot_name, anim_path))
        else:
            anim_path = '{}'.format(abc_name+'.abc')
            filename = os.path.normpath(os.path.join(out_folder, anim_path))

        anim_node = AlembicNode(browserutils.get_relative_path(filename, sp.get_solstice_project_path())[1:])
        abc_group_node.addChild(anim_node)
        for obj, geo_list in exports_dict.items():
            root_grp = AlembicExporterNode(obj)
            anim_node.addChild(root_grp)
            tag_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(obj)
            has_hires = sys.solstice.dcc.attribute_exists(node=tag_node, attribute_name='hires') if tag_node else None
            if tag_node and has_hires:
                hires_grp = sys.solstice.dcc.list_connections(node=tag_node, attribute_name='hires')
                if hires_grp and sys.solstice.dcc.object_exists(hires_grp[0]):
                    hires_node = AlembicExporterModelHires(hires_grp)
                    root_grp.addChild(hires_node)
                    for model in geo_list:
                        model_xform = sys.solstice.dcc.node_parent(node=model, full_path=True)
                        obj_is_visible = sys.solstice.dcc.get_attribute_value(node=model_xform, attribute_name='visibility')
                        if not obj_is_visible:
                            continue
                        obj_node = AlembicExporterNode(model)
                        hires_node.addChild(obj_node)
                else:
                    for geo in geo_list:
                        geo_node = AlembicExporterNode(geo)
                        root_grp.addChild(geo_node)
            else:
                for geo in geo_list:
                    geo_node = AlembicExporterNode(geo)
                    root_grp.addChild(geo_node)

        self.export_btn.setEnabled(True)

        self._abc_tree.expandAll()

    def _add_tag_attributes(self, attr_node, tag_node):
        # We add attributes to the first node in the list
        attrs = sys.solstice.dcc.list_user_attributes(tag_node)
        tag_info = dict()
        for attr in attrs:
            try:
                tag_info[attr] = str(sys.solstice.dcc.get_attribute_value(node=tag_info, attribute_name=attr))
            except Exception:
                pass
        if not tag_info:
            sys.solstice.logger.warning('Node has not valid tag data: {}'.format(tag_node))
            return

        if not sys.solstice.dcc.attribute_exists(node=attr_node, attribute_name='tag_info'):
            sys.solstice.dcc.add_string_attribute(node=attr_node, attribute_name='tag_info', keyable=True)
        sys.solstice.dcc.set_string_attribute_value(node=attr_node, attribute_name='tag_info', attribute_value=str(tag_info))

    def _get_tag_atributes_dict(self, tag_node):
        # We add attributes to the first node in the list
        tag_info = dict()
        if not tag_node:
            return tag_info

        attrs = sys.solstice.dcc.list_user_attributes(tag_node)
        for attr in attrs:
            try:
                tag_info[attr] = sys.solstice.dcc.get_attribute_value(node=tag_node, attribute_name=attr)
            except Exception:
                pass
        if not tag_info:
            sys.solstice.logger.warning('Node has not valid tag data: {}'.format(tag_node))
            return

        return tag_info

    def _get_alembic_rig_export_list(self, root_node):
        export_list = list()
        root_node_child_count = root_node.childCount()
        if root_node_child_count > 0 or len(sys.solstice.dcc.list_shapes(root_node.name)) > 0:
            for j in range(root_node.childCount()):
                c = root_node.child(j)
                c_name = c.name
                if type(c_name) in [list, tuple]:
                    c_name = c_name[0]
                if isinstance(c, AlembicExporterModelHires):
                    children = sys.solstice.dcc.node_children(node=c_name, all_hierarchy=True, full_path=True)
                    export_list.extend(children)
                    export_list.append(c_name)

                    # if tag_node:
                    #     self._add_tag_attributes(c_name, tag_node)
                    # export_list.append(c_name)
                else:
                    if 'transform' != sys.solstice.dcc.node_type(c_name):
                        xform = sys.solstice.dcc.node_parent(node=c_name, full_path=True)
                        parent_xform = sys.solstice.dcc.node_parent(node=xform, full_path=True)
                        if parent_xform:
                            children = sys.solstice.dcc.node_children(node=parent_xform, all_hierarchy=True, full_path=True)
                            export_list.extend(children)
                    else:
                        children = sys.solstice.dcc.node_children(node=c_name, all_hierarchy=True, full_path=True)
                        export_list.extend(children)

        for obj in reversed(export_list):
            if sys.solstice.dcc.node_type(obj) != 'transform':
                export_list.remove(obj)
                continue
            is_visible = sys.solstice.dcc.get_attribute_value(node=obj, attribute_name='visibility')
            if not is_visible:
                export_list.remove(obj)
                continue
            if sys.solstice.dcc.attribute_exists(node=obj, attribute_name='displaySmoothMesh'):
                sys.solstice.dcc.set_integer_attribute_value(node=obj, attribute_name='displaySmoothMesh', attribute_value=2)

        childs_to_remove = list()
        for obj in export_list:
            children = sys.solstice.dcc.node_children(node=obj, all_hierarchy=True, full_path=True)
            shapes = sys.solstice.dcc.list_children_shapes(node=obj, all_hierarchy=True, full_path=True)
            if children and not shapes:
                childs_to_remove.extend(children)

        if childs_to_remove:
            for obj in childs_to_remove:
                if obj in export_list:
                    export_list.remove(obj)

        return export_list

    def _export_alembics(self, alembic_nodes):

        def _recursive_hierarchy(transform):
            child_nodes = list()
            if not transform:
                return child_nodes
            transforms = cmds.listRelatives(transform, f=True)
            if not transforms:
                return child_nodes
            for eachTransform in transforms:
                if cmds.nodeType(eachTransform) == "transform":
                    child_nodes.append(eachTransform)
                    child_nodes.extend(_recursive_hierarchy(eachTransform))
            return child_nodes

        for n in alembic_nodes:
            export_path = n.get('path')
            abc_node = n.get('node')

            if os.path.isfile(export_path):
                res = sys.solstice.dcc.confirm_dialog(
                    title='Alembic File already exits!',
                    message='Are you sure you want to overwrite already existing Alembic File?\n\n{}'.format(export_path),
                    button=['Yes', 'No'],
                    default_button='Yes',
                    cancel_button='No',
                    dismiss_string='No'
                )
                if res != 'Yes':
                    sys.solstice.logger.debug('Aborting Alembic Export operation ...')
                    return

            export_list = list()
            all_nodes = list()
            tag_info = dict()

            child_count = abc_node.childCount()
            if not child_count:
                return

            for i in range(abc_node.childCount()):
                root_node = abc_node.child(i)
                root_node_name = root_node.name
                root_tag = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(root_node_name)
                root_tag_info = self._get_tag_atributes_dict(root_tag)
                if not root_tag_info:
                    sys.solstice.logger.warning('Impossible to retrieve tag info for {} ...'.format(root_node_name))
                    return
                tag_info[sys.solstice.dcc.node_short_name(root_node_name)] = root_tag_info
                hires_grp = sys.solstice.dcc.list_connections(node=root_tag, attribute_name='hires')
                if hires_grp and sys.solstice.dcc.object_exists(hires_grp[0]):
                    all_nodes.extend(_recursive_hierarchy(root_node_name))
                    export_list.extend(self._get_alembic_rig_export_list(root_node))
                else:
                    all_nodes.extend(_recursive_hierarchy(root_node_name))
                    export_list.extend(sys.solstice.dcc.list_children(root_node_name, all_hierarchy=False, full_path=True))

            for node in all_nodes:
                # if sys.solstice.dcc.node_is_referenced(node):
                #     raise RuntimeError('Alembic Exporter does not support references!')
                if sys.solstice.dcc.attribute_exists(node=node, attribute_name='displaySmoothMesh'):
                    sys.solstice.dcc.set_integer_attribute_value(node=node, attribute_name='displaySmoothMesh', attribute_value=2)

            if not export_list:
                sys.solstice.logger.debug('No geometry to export! Aborting Alembic Export operation ...')
                return

            # Retrieve all Arnold attributes to export from the first element of the list
            geo_shapes = sys.solstice.dcc.list_shapes(node=export_list)
            if not geo_shapes:
                children = sys.solstice.dcc.list_children(node=export_list, all_hierarchy=True, full_path=True)
                for child in children:
                    geo_shapes = sys.solstice.dcc.list_shapes(node=child)
                    if geo_shapes:
                        break
            if not geo_shapes:
                sys.solstice.logger.debug('No geometry data to export! Aborting Alembic Export operation ...')
                return
            geo_shape = geo_shapes[0]

            arnold_attrs = [attr for attr in sys.solstice.dcc.list_attributes(geo_shape) if attr.startswith('ai')]

            artellautils.lock_file(export_path, True)

            valid_alembic = alembic.export(
                root=export_list,
                alembicFile=export_path,
                frameRange=[[float(self.start.value()), float(self.end.value())]],
                userAttr=arnold_attrs,
                uvWrite=True,
                writeUVSets=True,
                writeCreases=True
            )
            if not valid_alembic:
                sys.solstice.logger.warning('Error while exporting Alembic file: {}'.format(export_path))
                return

            tag_json_file = os.path.join(os.path.dirname(export_path), abc_node.name.replace('.abc', '_abc.info')[1:])
            with open(tag_json_file, 'w') as f:
                json.dump(tag_info, f)

            if self.open_folder_after_export_cbx.isChecked():
                pythonutils.open_folder(os.path.dirname(export_path))

            for n in export_list:
                if sys.solstice.dcc.attribute_exists(node=n, attribute_name='tag_info'):
                    try:
                        sys.solstice.dcc.delete_attribute(node=n, attribute_name='tag_info')
                    except Exception as e:
                        pass

    def _on_export(self):

        out_folder = self.export_path_line.text()
        if not os.path.exists(out_folder):
            sys.solstice.dcc.confirm_dialog(
                title='Error during Alembic Exportation',
                message='Output Path does not exists: {}. Select a valid one!'.format(out_folder)
            )
            return

        abc_group_node = self._tree_model._root_node.child(0)
        if not sys.solstice.dcc.object_exists(abc_group_node.name):
            raise Exception('ERROR: Invalid Alembic Group: {}'.format(abc_group_node.name))
        if abc_group_node.childCount() == 0:
            raise Exception('ERROR: Selected Alembic Group has no objects to export!')

        file_paths = list()

        export_info = list()
        for i in range(abc_group_node.childCount()):
            child = abc_group_node.child(i)
            export_path = os.path.normpath(out_folder + child.name)
            file_paths.append(export_path)
            export_info.append({'path': export_path, 'node': child})

            # for j in range(root_tag_grp.childCount()):
            #     c = child.child(j)
            #     export_info[export_type]['path'] = export_path
        #

        res = sys.solstice.dcc.confirm_dialog(
            title='Export Alembic File',
            message='Are you sure you want to export Alembic to files?\n\n' + '\n'.join([p for p in file_paths]),
            button=['Yes', 'No'],
            default_button='Yes',
            cancel_button='No',
            dismiss_string='No'
        )
        if res != 'Yes':
            sys.solstice.logger.debug('Aborting Alembic Export operation ...')
            return

        self._export_alembics(export_info)


class AlembicImporter(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicImporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        buttons_layout = QGridLayout()
        self.main_layout.addLayout(buttons_layout)

        shot_name_lbl = QLabel('Shot Name: ')
        self.shot_line = QLineEdit()
        buttons_layout.addWidget(shot_name_lbl, 1, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.shot_line, 1, 1)
        shot_name_lbl.setVisible(False)
        self.shot_line.setVisible(False)

        folder_icon = resource.icon('open')
        alembic_path_layout = QHBoxLayout()
        alembic_path_layout.setContentsMargins(2, 2, 2, 2)
        alembic_path_layout.setSpacing(2)
        alembic_path_widget = QWidget()
        alembic_path_widget.setLayout(alembic_path_layout)
        alembic_path_lbl = QLabel('Alembic File: ')
        self.alembic_path_line = QLineEdit()
        self.alembic_path_line.setReadOnly(True)
        self.alembic_path_btn = QPushButton()
        self.alembic_path_btn.setIcon(folder_icon)
        self.alembic_path_btn.setIconSize(QSize(18, 18))
        self.alembic_path_btn.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        alembic_path_layout.addWidget(self.alembic_path_line)
        alembic_path_layout.addWidget(self.alembic_path_btn)
        buttons_layout.addWidget(alembic_path_lbl, 2, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(alembic_path_widget, 2, 1)

        import_mode_layout = QHBoxLayout()
        import_mode_layout.setContentsMargins(2, 2, 2, 2)
        import_mode_layout.setSpacing(2)
        import_mode_widget = QWidget()
        import_mode_widget.setLayout(import_mode_layout)
        import_mode_lbl = QLabel('Import mode: ')
        self.create_radio = QRadioButton('Create')
        self.add_radio = QRadioButton('Add')
        self.merge_radio = QRadioButton('Merge')
        self.create_radio.setChecked(True)
        import_mode_layout.addWidget(self.create_radio)
        import_mode_layout.addWidget(self.add_radio)
        import_mode_layout.addWidget(self.merge_radio)
        buttons_layout.addWidget(import_mode_lbl, 3, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(import_mode_widget, 3, 1)
        import_mode_lbl.setVisible(False)
        import_mode_widget.setVisible(False)

        auto_display_lbl = QLabel('Auto Display Smooth?: ')
        self.auto_smooth_display = QCheckBox()
        self.auto_smooth_display.setChecked(True)
        buttons_layout.addWidget(auto_display_lbl, 4, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.auto_smooth_display, 4, 1)

        self.main_layout.addLayout(splitters.SplitterLayout())

        self.merge_abc_widget = QWidget()
        self.merge_abc_widget.setVisible(False)
        merge_abc_layout = QVBoxLayout()
        merge_abc_layout.setContentsMargins(2, 2, 2, 2)
        merge_abc_layout.setSpacing(2)
        self.merge_abc_widget.setLayout(merge_abc_layout)
        self.main_layout.addWidget(self.merge_abc_widget)

        merge_abc_layout.addWidget(splitters.Splitter('Select Alembic Group to merge into'))

        alembic_set_lbl = QLabel('Alembic Groups')
        self.alembic_groups_combo = QComboBox()
        self.alembic_groups_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        abc_layout = QHBoxLayout()
        abc_layout.setContentsMargins(2, 2, 2, 2)
        abc_layout.setSpacing(2)
        abc_layout.addWidget(alembic_set_lbl)
        abc_layout.addWidget(self.alembic_groups_combo)
        merge_abc_layout.addLayout(abc_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(2, 2, 2, 2)
        buttons_layout.setSpacing(2)
        self.main_layout.addLayout(buttons_layout)
        import_btn = QPushButton('Import')
        import_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        reference_btn = QPushButton('Reference')
        reference_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        buttons_layout.addWidget(import_btn)
        buttons_layout.addWidget(reference_btn)

        self.create_radio.clicked.connect(self._on_mode_changed)
        self.add_radio.clicked.connect(self._on_mode_changed)
        self.merge_radio.clicked.connect(self._on_mode_changed)
        self.alembic_path_btn.clicked.connect(self._on_browse_alembic)
        import_btn.clicked.connect(self._on_import_alembic)
        reference_btn.clicked.connect(partial(self._on_import_alembic, True))

        self._on_mode_changed()

    def refresh(self):
        """
        Function that update necessary info of the tool
        """

        self._refresh_alembic_groups()
        self._refresh_shot_name()

    def _refresh_alembic_groups(self):
        """
        Internal function that updates the list of alembic groups
        """

        filtered_sets = filter(lambda x: x.endswith(ALEMBIC_GROUP_SUFFIX), sys.solstice.dcc.list_nodes(node_type='objectSet'))
        filtered_sets.insert(0, '')
        self.alembic_groups_combo.blockSignals(True)
        try:
            self.alembic_groups_combo.clear()
            self.alembic_groups_combo.addItems(filtered_sets)
        except Exception:
            pass
        self.alembic_groups_combo.blockSignals(False)

    def _refresh_shot_name(self):
        """
        Internal function that updates the shot name QLineEdit text
        """

        shot_name = 'Undefined'
        current_scene = sys.solstice.dcc.scene_name()
        if current_scene:
            current_scene = os.path.basename(current_scene)

        shot_regex = sp.get_solstice_shot_name_regex()
        m = shot_regex.match(current_scene)
        if m:
            shot_name = m.group(1)

        self.shot_line.setText(shot_name)

    def _on_mode_changed(self):
        self.merge_abc_widget.setVisible(self.merge_radio.isChecked())

    def _on_browse_alembic(self):

        shot_name = self.shot_line.text()
        abc_folder = os.path.normpath(os.path.join(sp.get_solstice_project_path(), shot_name)) if shot_name != 'unresolved' else sp.get_solstice_project_path()

        pattern = 'Alembic Files (*.abc)'
        if sp.is_houdini():
            pattern = '*.abc'
        abc_file = sys.solstice.dcc.select_file_dialog(title='Select Alembic to Import', start_directory=abc_folder, pattern=pattern)
        if abc_file:
            self.alembic_path_line.setText(abc_file)

    @classmethod
    def import_alembic(cls, alembic_path, parent=None):
        if not alembic_path or not os.path.isfile(alembic_path):
            sys.solstice.logger.warning('Alembic file {} does not exits!'.format(alembic_path))
            return None

        tag_json_file = os.path.join(os.path.dirname(alembic_path), os.path.basename(alembic_path).replace('.abc', '_abc.info'))
        valid_tag_info = True
        if os.path.isfile(tag_json_file):
            with open(tag_json_file, 'r') as f:
                tag_info = json.loads(f.read())
            if not tag_info:
                sys.solstice.logger.warning('No Alembic Info loaded!')
                valid_tag_info = False
        else:
            sys.solstice.logger.warning('No Alembic Info file found! Take into account that imported Alembic is not supported by our current pipeline!')
            valid_tag_info = False

        if sp.is_houdini():
            import hou
            n = hou.node('obj')
            parent = n.createNode('alembicarchive')
        if parent and valid_tag_info:
            cls._add_tag_info_data(tag_info=tag_info, attr_node=parent)

        alembic.import_alembic(alembic_path, mode='import', nodes=None, parent=parent)

    @staticmethod
    def reference_alembic(alembic_path, namespace=None):

        if not sp.is_maya():
            sys.solstice.logger.warning('DCC {} does not supports the reference of Alembic groups!'.format(sys.solstice.dcc.get_name()))
            return None

        if not alembic_path or not os.path.isfile(alembic_path):
            sys.solstice.logger.warning('Alembic file {} does not exits!'.format(alembic_path))
            return None

        abc_name = os.path.basename(alembic_path).split('.')[0]
        tag_json_file = os.path.join(os.path.dirname(alembic_path), os.path.basename(alembic_path).replace('.abc', '_abc.info'))
        if not os.path.isfile(tag_json_file):
            sys.solstice.logger.warning('No Alembic Info file found!')
            return

        with open(tag_json_file, 'r') as f:
            tag_info = json.loads(f.read())
        if not tag_info:
            sys.solstice.logger.warning('No Alembic Info loaded!')
            return

        root = cmds.group(n=abc_name, empty=True, world=True)
        AlembicImporter._add_tag_info_data(tag_info, root)
        sel = [root]
        sel = sel or None

        track_nodes = mayautils.TrackNodes()
        track_nodes.load()

        if not namespace:
            namespace = abc_name

        valid_reference = alembic.reference_alembic(alembic_path, namespace=namespace)
        if not valid_reference:
            sys.solstice.logger.warning('Error while reference Alembic file: {}'.format(alembic_path))
            return
        res = track_nodes.get_delta()
        for obj in res:
            if not sys.solstice.dcc.object_exists(obj):
                continue
            if not sys.solstice.dcc.node_type(obj) == 'transform':
                continue
            obj_parent = sys.solstice.dcc.node_parent(obj)
            if obj_parent:
                continue
            sys.solstice.dcc.set_parent(obj, sel[0])

    def _on_import_alembic(self, as_reference=False):

        if sp.is_maya():
            import maya.cmds as cmds
        elif sp.is_houdini():
            import hou

        abc_file = self.alembic_path_line.text()
        if not abc_file or not os.path.isfile(abc_file):
            sys.solstice.dcc.confirm_dialog(title='Error', message='No Alembic File is selected or file is not currently available in disk')
            return None

        sel_set = self.alembic_groups_combo.currentText()
        if self.merge_radio.isChecked() and not sel_set:
            sys.solstice.dcc.confirm_dialog(title='Error', message='No Alembic Group selected. Please create the Alembic Group first and retry')
            return None

        nodes = None
        if sp.is_maya() and sel_set:
            nodes = sorted(cmds.sets(sel_set, query=True, no=True))

        abc_name = os.path.basename(abc_file).split('.')[0]
        tag_json_file = os.path.join(os.path.dirname(abc_file), os.path.basename(abc_file).replace('.abc', '_abc.info'))
        valid_tag_info = True
        if os.path.isfile(tag_json_file):
            with open(tag_json_file, 'r') as f:
                tag_info = json.loads(f.read())
            if not tag_info:
                sys.solstice.logger.warning('No Alembic Info loaded!')
                valid_tag_info = False
        else:
            sys.solstice.logger.warning('No Alembic Info file found!')
            valid_tag_info = False
        if not valid_tag_info:
            return

        root_to_add = None
        if self.create_radio.isChecked():
            if sp.is_maya():
                root = cmds.group(n=abc_name, empty=True, world=True)
                root_to_add = root
            elif sp.is_houdini():
                n = hou.node('obj')
                root = n.createNode('alembicarchive')
                root_to_add = root
            # if valid_tag_info:
            #     self._add_tag_info_data(tag_info, root)
            sel = [root]
        else:
            sel = sys.solstice.dcc.selected_nodes(full_path=True)
            if not sel:
                sel = cmds.group(n=abc_name, empty=True, world=True)
                root_to_add = sel
                # if valid_tag_info:
                #     self._add_tag_info_data(tag_info, sel)

        sel = sel or None

        if sp.is_maya():
            track_nodes = mayautils.TrackNodes()
            track_nodes.load()

        if as_reference:
            if sp.is_maya():
                valid_reference = alembic.reference_alembic(abc_file, namespace=abc_name)
                if not valid_reference:
                    sys.solstice.logger.warning('Error while reference Alembic file: {}'.format(abc_file))
                    return
                res = track_nodes.get_delta()
                for obj in res:
                    if not sys.solstice.dcc.object_exists(obj):
                        continue
                    if not sys.solstice.dcc.node_type(obj) == 'transform':
                        continue
                    obj_parent = sys.solstice.dcc.node_parent(obj)
                    if obj_parent:
                        continue
                    sys.solstice.dcc.set_parent(node=obj, parent=sel[0])
            else:
                sys.solstice.logger.warning('Alembic Reference is only supported in Maya!')
                return None
        else:
            res = alembic.import_alembic(abc_file, mode='import', nodes=nodes, parent=sel[0])
            res = [res]
            if sp.is_maya():
                res = track_nodes.get_delta()

        added_tag = False
        for key in tag_info.keys():
            for obj in res:
                short_obj = sys.solstice.dcc.node_short_name(obj)
                if key == short_obj:
                    self._add_tag_info_data(tag_info[key], obj)
                    added_tag = True
                elif '{}_hires_grp'.format(key) == short_obj:
                    self._add_tag_info_data(tag_info[key], obj)
                    added_tag = True

        if not added_tag and root_to_add:
            self._add_tag_info_data(tag_info, root_to_add)

        if self.auto_smooth_display.isChecked():
            for obj in res:
                if obj and sys.solstice.dcc.object_exists(obj):
                    if sys.solstice.dcc.node_type(obj) == 'shape':
                        if sys.solstice.dcc.attribute_exists(node=obj, attribute_name='aiSubdivType'):
                            cmds.setAttr('{}.aiSubdivType '.format(obj), 1)
                    elif sys.solstice.dcc.node_type(obj) == 'transform':
                        shapes = sys.solstice.dcc.list_shapes(node=obj, full_path=True)
                        if not shapes:
                            continue
                        for s in shapes:
                            if sys.solstice.dcc.attribute_exists(node=s, attribute_name='aiSubdivType'):
                                cmds.setAttr('{}.aiSubdivType '.format(s), 1)

        return res

    @staticmethod
    def _add_tag_info_data(tag_info, attr_node):
        if sp.is_maya():
            if not sys.solstice.dcc.attribute_exists(node=attr_node, attribute_name='tag_info'):
                sys.solstice.dcc.add_string_attribute(node=attr_node, attribute_name='tag_info', keyable=True)
            sys.solstice.dcc.set_string_attribute_value(node=attr_node, attribute_name='tag_info', attribute_value=str(tag_info))
        elif sp.is_houdini():
            import hou
            parm_group = attr_node.parmTemplateGroup()
            parm_folder = hou.FolderParmTemplate('folder', 'Solstice Info')
            parm_folder.addParmTemplate(hou.StringParmTemplate('tag_info', 'Tag Info', 1))
            parm_group.append(parm_folder)
            attr_node.setParmTemplateGroup(parm_group)
            attr_node.parm('tag_info').set(str(tag_info))


class AlembicManager(window.Window, object):
    name = 'Solstice_AlembicManager'
    title = 'Solstice Tools - Alembic Manager'
    version = '1.2'

    def __init__(self):
        super(AlembicManager, self).__init__()

        if sp.is_maya():
            import maya.OpenMaya as OpenMaya
            self.add_callback(OpenMaya.MEventMessage.addEventCallback('SelectionChanged', self._on_selection_changed, self))

    def custom_ui(self):
        super(AlembicManager, self).custom_ui()

        self.set_logo('solstice_alembicmanager_logo')

        self.resize(400, 600)

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.alembic_group = AlembicGroup()
        self.alembic_importer = AlembicImporter()
        self.alembic_exporter = AlembicExporter()

        self.main_tabs.addTab(self.alembic_group, 'Alembic Group')
        self.main_tabs.addTab(self.alembic_exporter, 'Exporter')
        self.main_tabs.addTab(self.alembic_importer, 'Importer')

        self.main_tabs.currentChanged.connect(self._on_change_tab)

    def _on_change_tab(self, tab_index):
        if tab_index == 1:
            self.alembic_exporter.refresh()

    def _on_selection_changed(self, *args, **kwargs):
        if self.main_tabs.currentIndex() == 1:
            self.alembic_exporter._refresh_alembic_groups()


def run():
    AlembicManager().show()
