#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_standinmanager.py
# by Tomas Poveda
# Tool to export/import Arnold Standin (.ass) files
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
from functools import partial

import maya.cmds as cmds

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters, solstice_buttons
from solstice_pipeline.solstice_utils import solstice_maya_utils
from solstice_pipeline.resources import solstice_resource


class StandinImporter(QWidget, object):
    def __init__(self, parent=None):
        super(StandinImporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        buttons_layout = QGridLayout()
        self.main_layout.addLayout(buttons_layout)

        folder_icon = solstice_resource.icon('open')
        standin_path_layout = QHBoxLayout()
        standin_path_layout.setContentsMargins(2, 2, 2, 2)
        standin_path_layout.setSpacing(2)
        standin_path_widget = QWidget()
        standin_path_widget.setLayout(standin_path_layout)
        standin_path_lbl = QLabel('Standin File: ')
        self.standin_path_line = QLineEdit()
        self.standin_path_line.setReadOnly(True)
        self.standin_path_btn = QPushButton()
        self.standin_path_btn.setIcon(folder_icon)
        self.standin_path_btn.setIconSize(QSize(18, 18))
        self.standin_path_btn.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        standin_path_layout.addWidget(self.standin_path_line)
        standin_path_layout.addWidget(self.standin_path_btn)
        buttons_layout.addWidget(standin_path_lbl, 1, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(standin_path_widget, 1, 1)

        self.import_btn = QPushButton('Import')
        self.import_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.reference_btn = QPushButton('Reference')
        buttons_layout.addWidget(self.import_btn, 2, 0, 2, 2)
        self.import_btn.setEnabled(False)

        self.standin_path_btn.clicked.connect(self._on_browse_standin)
        self.standin_path_line.textChanged.connect(self.refresh)
        self.import_btn.clicked.connect(self._on_import)

    @staticmethod
    def import_standin(standin_path, standin_name=None):
        if not standin_path or not os.path.isfile(standin_path):
            sp.logger.warning('Alembic file {} does not exits!'.format(standin_path))
            return None

        if standin_name is None:
            standin_name = os.path.basename(standin_path).split('.')[0]

        standin_node = cmds.createNode('aiStandIn', name='{}_standin'.format(standin_name))
        xform = cmds.listRelatives(standin_node, parent=True)[0]
        cmds.rename(xform, standin_name)
        cmds.setAttr('{}.dso'.format(standin_node), standin_path, type='string')

    def refresh(self):
        if self.standin_path_line.text() and os.path.isfile(self.standin_path_line.text()):
            self.import_btn.setEnabled(True)
        else:
            self.import_btn.setEnabled(False)

    def _on_browse_standin(self):

        standin_folder = sp.get_solstice_project_path()

        res = cmds.fileDialog2(fm=1, dir=standin_folder, cap='Select Standin to Import', ff='Standin Files (*.ass)')
        if res:
            standin_file = res[0]
        else:
            standin_file = ''

        self.standin_path_line.setText(standin_file)

        self.refresh()

    def _on_import(self):
        standin_file = self.standin_path_line.text()
        if not standin_file or not os.path.isfile(standin_file):
            cmds.confirmDialog(t='Error', m='No Standin File is selected or file is not currently available on disk')
            return None

        standin_name = os.path.basename(standin_file).split('.')[0]

        self.import_standin(standin_file, standin_name)


class StandinExporter(QWidget, object):
    def __init__(self, parent=None):
        super(StandinExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        buttons_layout = QGridLayout()
        self.main_layout.addLayout(buttons_layout)

        name_lbl = QLabel('Standin Name: ')
        self.name_line = QLineEdit()
        self.name_line_btn = solstice_buttons.IconButton(icon_name='double_left', icon_hover='double_left_hover')
        buttons_layout.addWidget(name_lbl, 1, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.name_line, 1, 1)
        buttons_layout.addWidget(self.name_line_btn, 1, 2)

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
        self.export_path_btn.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        export_path_layout.addWidget(self.export_path_line)
        export_path_layout.addWidget(self.export_path_btn)
        buttons_layout.addWidget(export_path_lbl, 4, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(export_path_widget, 4, 1)

        auto_sync_shaders_lbl = QLabel('Auto Sync Shaders?: ')
        self.auto_sync_shaders = QCheckBox()
        self.auto_sync_shaders.setChecked(True)
        buttons_layout.addWidget(auto_sync_shaders_lbl, 5, 0, 1, 1, Qt.AlignRight)
        buttons_layout.addWidget(self.auto_sync_shaders, 5, 1)

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        export_layout = QHBoxLayout()
        self.export_btn = QPushButton('Export')
        self.export_btn.setEnabled(False)
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        export_layout.addWidget(self.export_btn)
        export_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.main_layout.addLayout(export_layout)

        self.name_line.textChanged.connect(self.refresh)
        self.export_path_btn.clicked.connect(self._on_set_export_path)
        self.export_btn.clicked.connect(self._on_export)
        self.name_line_btn.clicked.connect(partial(self._get_selected, self.name_line))

        self.refresh()

    def refresh(self):
        self._refresh_standin_name()
        self._refresh_frame_ranges()

        if self.export_path_line.text() and os.path.isdir(self.export_path_line.text()):
            self.export_btn.setEnabled(True)
        else:
            self.export_btn.setEnabled(False)

    def export_standin(self, export_path, standin_name, start_frame=1, end_frame=1):
        if not export_path or not os.path.isdir(export_path):
            sp.logger.warning('Impossible to export Standin in invalid path: {}'.format(export_path))
            return None

        self.name_line.setText(standin_name)
        self.start.setValue(start_frame)
        self.end.setValue(end_frame)
        self.export_path_line.setText(export_path)
        self._on_export()

    def _refresh_standin_name(self):
        """
        Internal function that updates Alembic name
        """

        if self.name_line.text() != '':
            return

        sel = cmds.ls(sl=True)
        if sel:
            sel = sel[0]
            is_referenced = cmds.referenceQuery(sel, isNodeReferenced=True)
            if is_referenced:
                sel_namespace = cmds.referenceQuery(sel, namespace=True)
                if not sel_namespace or not sel_namespace.startswith(':'):
                    pass
                else:
                    sel_namespace = sel_namespace[1:] + ':'
                    sel = sel.replace(sel_namespace, '')

            self.name_line.setText(sel)

    def _refresh_frame_ranges(self):
        """
        Internal function that updates the frame ranges values
        """

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame=cmds.playbackOptions(q=True, max=True)
        self.start.setValue(int(start_frame))
        self.end.setValue(int(end_frame))

    def _get_selected(self, line_widget):
        sel = cmds.ls(sl=True, l=True)
        if not sel:
            sp.logger.warning('Please select a object first!')
            return
        if len(sel) > 1:
            sp.logger.warning('You have selected more than one object. First item in the selection will be used ...')
        sel = sel[0]
        if sel.startswith('|'):
            sel = sel[1:]

        uuid = cmds.ls(sel, uuid=True)
        self._target = uuid
        short = cmds.ls(sel)[0]

        line_widget.clear()
        line_widget.setText(short)

        self.refresh()

        return sel

    def _on_set_export_path(self):
        """
        Internal function that is calledd when the user selects the folder icon
        Allows the user to select a path to export Alembic group contents
        """

        assets_path = sp.get_solstice_assets_path()
        start_dir = sp.get_solstice_assets_path()

        if self.name_line.text():
            for asset_type in sp.asset_types:
                asset_type = asset_type.replace(' ', '')
                asset_path = os.path.join(assets_path, asset_type, self.name_line.text(), '__working__', 'model')
                if os.path.exists(assets_path):
                    start_dir = os.path.dirname(asset_path)
                    break

        res = cmds.fileDialog2(fm=3, dir=start_dir, cap='Select Alembic Export Folder')
        if not res:
            return

        export_folder = res[0]
        self.export_path_line.setText(export_folder)

    def _on_export(self):

        from solstice_pipeline.solstice_tools import solstice_shaderlibrary
        reload(solstice_shaderlibrary)

        out_folder = self.export_path_line.text()
        if not os.path.exists(out_folder):
            cmds.confirmDialog(
                t='Error during Standin Exportation',
                m='Output Path does not exists: {}. Select a valid one!'.format(out_folder)
            )
            return

        standin_file = os.path.join(out_folder, self.name_line.text()+'.ass')
        bbox_file = os.path.join(out_folder, self.name_line.text()+'.asstoc')
        # arnold_files = [standin_file, bbox_file]
        arnold_files = [standin_file]

        if not self.auto_sync_shaders.isChecked():
            res = cmds.confirmDialog(
                t='Exporting Standin',
                m='Make sure that your asset has proper shaders applied to it! Do you want to continue?',
                button=['Yes', 'No'],
                defaultButton='Yes',
                cancelButton='No',
                dismissString='No',
                icon='warning'
            )
            if res != 'Yes':
                sp.logger.debug('Aborting Standin Export operation ...')
                return

        res = cmds.confirmDialog(
            t='Exporting Standin File: {}'.format(out_folder),
            m='Are you sure you want to export standin files?\n\n' + '\n'.join([os.path.basename(f) for f in arnold_files]),
            button=['Yes', 'No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
        )

        if res != 'Yes':
            sp.logger.debug('Aborting Standin Export operation ...')
            return

        if os.path.isfile(standin_file):
            res = cmds.confirmDialog(
                t='Alembic File already exits!',
                m='Are you sure you want to overwrite exising Alembic file?\n\n{}'.format(standin_file),
                button=['Yes', 'No'],
                defaultButton='Yes',
                cancelButton='No',
                dismissString='No'
            )
            if res != 'Yes':
                sp.logger.debug('Aborting Alembic Export operation ...')
                return

        sel = cmds.ls(sl=True)

        if self.auto_sync_shaders.isChecked():
            solstice_shaderlibrary.ShaderLibrary.load_scene_shaders()

        start_frame = self.start.value()
        end_frame = self.end.value()
        if end_frame < start_frame:
            end_frame = start_frame
        if start_frame == end_frame:
            if sel:
                cmds.arnoldExportAss(
                    filename=standin_file,
                    s=True,
                    shadowLinks=1,
                    mask=2303,
                    ll=1,
                    boundingBox=True
                )
            else:
                cmds.arnoldExportAss(
                    self.name_line.text(),
                    filename=standin_file,
                    shadowLinks=1,
                    mask=2303,
                    ll=1,
                    boundingBox=True
                )
        else:
            if sel:
                cmds.arnoldExportAss(
                    filename=standin_file,
                    s=True,
                    shadowLinks=1,
                    mask=2303,
                    ll=1,
                    boundingBox=True,
                    startFrame=start_frame,
                    endFrame=end_frame,
                    frameStep=1.0
                )
            else:
                cmds.arnoldExportAss(
                    self.name_line.text(),
                    filename=standin_file,
                    shadowLinks=1,
                    mask=2303,
                    ll=1,
                    boundingBox=True,
                    startFrame=start_frame,
                    endFrame=end_frame,
                    frameStep=1.0
                )
            cmds.currentTime(start_frame, edit=True)


class StandinManager(solstice_windows.Window, object):
    name = 'SolsticeStandinManager'
    title = 'Solstice Tools - Standin Manager'
    version = '1.1'

    def __init__(self):
        super(StandinManager, self).__init__()

    def custom_ui(self):
        super(StandinManager, self).custom_ui()

        self.set_logo('solstice_standinmanager_logo')

        self.resize(400, 600)

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        alembic_importer = StandinImporter()
        alembic_exporter = StandinExporter()

        self.main_tabs.addTab(alembic_exporter, 'Exporter')
        self.main_tabs.addTab(alembic_importer, 'Importer')

def run():
    win = StandinManager().show()
