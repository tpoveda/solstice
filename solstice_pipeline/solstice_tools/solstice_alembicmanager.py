#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_alembicmanager.py
# by Tomas Poveda
# Tool to export/import Alembic (.abc) files
# ______________________________________________________________________
# ==================================================================="""

import os
import sys

import maya.cmds as cmds

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters
from solstice_pipeline.resources import solstice_resource

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

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(25, 5, 25, 5)
        self.main_layout.addLayout(buttons_layout)

        create_btn = QPushButton('Create')
        buttons_layout.addWidget(create_btn)
        buttons_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Expanding))
        clean_alembic_groups_btn = QPushButton('Clean Alembic Groups')
        self.main_layout.addWidget(clean_alembic_groups_btn)

        create_btn.clicked.connect(self.create_alembic_group)

    def get_alembic_group_name_from_node_name(self, node_name):
        """
        Returns an alembic group name from the give node name
        :param node_name: str, long name of a Maya node
        :return: str
        """

        return node_name.split('|')[1].rsplit(':',1)[-1]

    def create_alembic_group(self, name=None, filter_type='transform'):
        """
        Creates a new alembic group (set)
        :param name: str, name of the alembic group
        :param filter_type:
        :return: str, new alembic group created
        """

        sel = cmds.ls(sl=True, l=True)
        if not sel:
            cmds.confirmDialog(t='Impossible to create Alembic Group',
                               m='No nodes selected, please select nodes first and try again!')
            return None

        if name is None:
            name = self.name_line.text()
            if not name:
                name = self.get_alembic_group_name_from_node_name(sel[0])

        if not name.endswith(ALEMBIC_GROUP_SUFFIX):
            name += ALEMBIC_GROUP_SUFFIX

        if cmds.objExists(name):
            res = cmds.confirmDialog(title='Alembic Group already exists!',
                                     message='Do you want to overwrite existing Alembic Group?',
                                     button=['Yes', 'No'],
                                     defaultButton='Yes',
                                     cancelButton='No',
                                     dismissString='No')
            if res and res == 'Yes':
                cmds.delete(name)

        sp.logger.debug('Creating Alembic Group with name: {}'.format(name))

        full_sel = cmds.listRelatives(sel, ad=True, f=True) or []
        main_sel = list()
        for n in full_sel:
            p = cmds.listRelatives(n, parent=True, f=True)
            p = p[0] if p else None
            if p and p in full_sel:
                continue
            main_sel.append(n)

        final_sel = None
        if filter_type:
            final_sel = filter(lambda x: cmds.objectType(x, isType=filter_type), main_sel)
        if final_sel is None:
            cmds.confirmDialog(t='Impossible to create Alembic Group',
                               m='No objects found with filter type: {}!'.format(filter_type))

        return cmds.sets(sel, n=name)


# ===================================================================================================================

class AlembicImporter(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicImporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)


# ===================================================================================================================



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

        shot_name_lbl = QLabel('Shot Name: ')
        self.shot_line = QLineEdit()
        buttons_layout.addWidget(shot_name_lbl, 1, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.shot_line, 1, 1)

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
        buttons_layout.addWidget(frame_range_lbl, 2, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(frame_range_widget, 2, 1)

        folder_icon = solstice_resource.icon('open')
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
        buttons_layout.addWidget(export_path_lbl, 3, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(export_path_widget, 3, 1)

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        export_layout = QHBoxLayout()
        export_btn = QPushButton('Export')
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        export_layout.addWidget(export_btn)
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.main_layout.addLayout(export_layout)

        self.export_path_btn.clicked.connect(self._on_set_export_path)
        export_btn.clicked.connect(self._on_export)

    def refresh(self):
        """
        Function that update necessary info of the tool
        Function that update necessary info of the tool
        """

        self._refresh_alembic_groups()
        self._refresh_frame_ranges()
        self._refresh_shot_name()

    def _refresh_alembic_groups(self):
        """
        Internal function that updates the list of alembic groups
        """

        filtered_sets = filter(lambda x: x.endswith(ALEMBIC_GROUP_SUFFIX), cmds.ls(type='objectSet'))
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

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame=cmds.playbackOptions(q=True, max=True)
        self.start.setValue(int(start_frame))
        self.end.setValue(int(end_frame))

    def _refresh_shot_name(self):
        """
        Internal function that updates the shot name QLineEdit text
        """

        shot_name = 'Undefined'
        current_scene = cmds.file(q=True, sn=True)
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

        res = cmds.fileDialog2(fm=3, dir=sp.get_solstice_project_path(), cap='Select Alembic Export Folder')
        if not res:
            return

        export_folder = res[0]
        self.export_path_line.setText(export_folder)

    def _on_export(self):
        sel_set = self.alembic_groups_combo.currentText()
        if not sel_set:
            cmds.confirmDialog(
                t='Error during Alembic Exportation',
                m='No Alembic Group selected. Please select an Alembic Group from the list'
            )
            return None

        set_nodes = cmds.sets(sel_set, q=True, no=True)
        if not set_nodes:
            cmds.confirmDialog(
                t='Error during Alembic Exportation',
                m='No members inside selected Alembic Group\n Alembic Group: {}'.format(sel_set)
            )

        set_nodes = sorted(set_nodes)

        shot_name = self.shot_line.text()
        if not shot_name:
            cmds.confirmDialog(
                t='Error during Alembic Exportation',
                m='Invalid shot name: {}! Please write a valid Solstice Short Name or load a valid shot scene and try again!'.format(shot_name)
            )
            return

        start_frame = str(self.start.value())
        end_frame = str(self.end.value())

        out_folder = self.export_path_line.text()
        if not os.path.exists(out_folder):
            cmds.confirmDialog(
                t='Error during Alembic Exportation',
                m='Output Path does not exists: {}. Select a valid one!'.format(out_folder)
            )
            return

        sp.logger.debug('Export Nodes:')
        sp.logger.debug('\tNodes: {}'.format(set_nodes))
        sp.logger.debug('\tFrame Range: {} - {}'.format(start_frame, end_frame))
        sp.logger.debug('\tOutput Folder: {}'.format(out_folder))

        if not ALEMBIC_GROUP_SUFFIX in sel_set:
            raise Exception('ERROR: Invalid Alembic Group: {}'.format(sel_set))

        out_filename = '{}_{}'.format(shot_name, sel_set.replace(ALEMBIC_GROUP_SUFFIX, '.abc'))
        filename = os.path.normpath(os.path.join(out_folder, shot_name, out_filename))

        res = cmds.confirmDialog(
            t='Exporting Alembic File',
            m='Are you sure you want to export alembic to file?\n\n{}'.format(filename),
            button=['Yes', 'No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
        )

        if res != 'Yes':
            sp.logger.debug('Aborting Alembic Export operation ...')
            return

        if os.path.isfile(filename):
            res = cmds.confirmDialog(
                t='Alembic File already exits!',
                m='Are you sure you want to overwrite exising Alembic file?\n\n{}'.format(filename),
                button=['Yes', 'No'],
                defaultButton='Yes',
                cancelButton='No',
                dismissString='No'
            )
            if res != 'Yes':
                sp.logger.debug('Aborting Alembic Export operation ...')
                return

        print('EXPORTINGNGNGG')


class AlembicManager(solstice_windows.Window, object):
    name = 'Solstice_AlembicManager'
    title = 'Solstice Tools - Alembic Manager'
    version = '1.0'

    def __init__(self):
        super(AlembicManager, self).__init__()

    def custom_ui(self):
        super(AlembicManager, self).custom_ui()

        self.set_logo('solstice_alembicmanager_logo')

        main_tabs = QTabWidget()
        self.main_layout.addWidget(main_tabs)

        self.alembic_group = AlembicGroup()
        self.alembic_importer = AlembicImporter()
        self.alembic_exporter = AlembicExporter()

        main_tabs.addTab(self.alembic_group, 'Alembic Group')
        main_tabs.addTab(self.alembic_exporter, 'Exporter')
        main_tabs.addTab(self.alembic_importer, 'Importer')

        main_tabs.currentChanged.connect(self._on_change_tab)

    def _on_change_tab(self, tab_index):
        if tab_index == 1:
            self.alembic_exporter.refresh()


def run():
    win = AlembicManager().show()
