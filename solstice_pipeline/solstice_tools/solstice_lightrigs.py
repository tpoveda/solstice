#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_light_rigs.py
# by Tomas Poveda
# Tool to manage Solstice Light Rigs
# ______________________________________________________________________
# ==================================================================="""

import os

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_sync_dialog, solstice_splitters
from solstice_pipeline.resources import solstice_resource

# ===============================================================================================

_import_icon = solstice_resource.icon('import')
_reference_icon = solstice_resource.icon('reference')
_open_icon = solstice_resource.icon('open')

# ===============================================================================================


class LightRig(QWidget, object):
    def __init__(self, name, parent=None):
        super(LightRig, self).__init__(parent=parent)

        self.name = name

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        self.setMaximumSize(QSize(120, 140))
        self.setMinimumSize(QSize(120, 140))

        self.light_btn = QPushButton()
        self.light_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.title_lbl = QLabel(self.name)
        self.title_lbl.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.light_btn)
        main_layout.addWidget(self.title_lbl)

        self.light_menu = QMenu(self)
        open_action = QAction(_open_icon, 'Open Light Rig', self.light_menu)
        import_action = QAction(_import_icon, 'Import Light Rig', self.light_menu)
        reference_action = QAction(_reference_icon, 'Reference Light Rig', self.light_menu)
        self.light_menu.addAction(open_action)
        self.light_menu.addAction(import_action)
        self.light_menu.addAction(reference_action)

        self.light_btn.clicked.connect(self._on_open_light_rig)
        open_action.triggered.connect(self._on_open_light_rig)
        import_action.triggered.connect(self._on_import_light_rig)
        reference_action.triggered.connect(self._on_reference_light_rig)

    def contextMenuEvent(self, event):
        self.light_menu.exec_(event.globalPos())

    def _on_open_light_rig(self):
        LightRigManager.open_light_rig(name=self.name)

    def _on_import_light_rig(self):
        LightRigManager.import_light_rig(name=self.name)

    def _on_reference_light_rig(self):
        LightRigManager.reference_light_rig(name=self.name)


class LightRigManager(solstice_windows.Window, object):

    name = 'SolsticeLightRigManager'
    title = 'Solstice Tools - Light Rigs Manager'
    version = '1.0'

    def __init__(self):
        super(LightRigManager, self).__init__()

    def custom_ui(self):
        super(LightRigManager, self).custom_ui()

        self.set_logo('solstice_lightrigs_logo')

        self.resize(100, 150)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        self.main_layout.addLayout(buttons_layout)

        open_btn = QToolButton()
        open_btn.setIcon(solstice_resource.icon('open'))
        sync_btn = QToolButton()
        sync_btn.setIcon(solstice_resource.icon('sync'))
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
        buttons_layout.addWidget(sync_btn)
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        self.light_rigs_layout = QHBoxLayout()
        self.light_rigs_layout.setContentsMargins(5, 5, 5, 5)
        self.light_rigs_layout.setSpacing(5)
        self.light_rigs_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.light_rigs_layout)

        self._update_ui()

    @staticmethod
    def get_solstice_light_rigs_path(sync=False):
        """
        Returns Solstice Light Rigs path
        :return: str
        """

        light_rigs_path = os.path.join(sp.get_solstice_assets_path(), 'lighting', 'Light Rigs')
        if sync:
            solstice_sync_dialog.SolsticeSyncPath(paths=[light_rigs_path]).sync()
        if os.path.exists(light_rigs_path):
            sp.logger.debug('Getting Light Rigs Path: {0}'.format(light_rigs_path))
            return light_rigs_path
        else:
            sp.logger.error('Impossible to sync light rigs! Please contact TD!')
            return None

    def _update_ui(self):
        valid_light_rigs = self.get_solstice_light_rigs_path()
        if not valid_light_rigs:
            return
        working_path = os.path.join(valid_light_rigs, '__working__')
        if not os.path.exists(working_path):
            return

        for f in os.listdir(working_path):
            light_rig = LightRig(name=f)
            self.light_rigs_layout.addWidget(light_rig)

    @staticmethod
    def open_light_rig(name):
        if cmds.file(query=True, modified=True):
            cmds.SaveScene()

        light_rigs_path = LightRigManager.get_solstice_light_rigs_path(sync=False)
        light_rig = os.path.join(light_rigs_path, '__working__', name.title(), 'LR_{}.ma'.format(name.title()).replace(' ', '_'))
        if not os.path.exists(light_rig):
            sp.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, o=True, f=True)

    @staticmethod
    def import_light_rig(name):
        if cmds.file(query=True, modified=True):
            cmds.SaveScene()

        light_rigs_path = LightRigManager.get_solstice_light_rigs_path(sync=False)
        light_rig = os.path.join(light_rigs_path, '__working__', name.title(), 'LR_{}.ma'.format(name.title()).replace(' ', '_'))
        if not os.path.exists(light_rig):
            sp.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, i=True, f=True)

    @staticmethod
    def reference_light_rig(name):
        if cmds.file(query=True, modified=True):
            cmds.SaveScene()

        light_rigs_path = LightRigManager.get_solstice_light_rigs_path(sync=False)
        light_rig = os.path.join(light_rigs_path, '__working__', name.title(),
                                 'LR_{}.ma'.format(name.title()).replace(' ', '_'))
        if not os.path.exists(light_rig):
            sp.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, reference=True, f=True)


def run():
    win = LightRigManager().show()
