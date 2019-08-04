#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to manage Solstice Light Rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys

from Qt.QtWidgets import *
from Qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.core import syncdialog
from solstice.pipeline.gui import window, splitters
from solstice.pipeline.utils import pythonutils, qtutils
from solstice.pipeline.resources import resource

if sp.is_maya():
    import maya.cmds as cmds

# ===============================================================================================

_import_icon = resource.icon('import')
_reference_icon = resource.icon('reference')
_open_icon = resource.icon('open')

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

        self.light_btn = QToolButton()
        self.light_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.light_btn.setIcon(resource.icon(name.lower()))
        self.light_btn.setIconSize(QSize(120, 140))
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

        self.light_btn.clicked.connect(self._on_reference_light_rig)
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


class LightRigManager(window.Window, object):

    name = 'SolsticeLightRigManager'
    title = 'Solstice Tools - Light Rigs Manager'
    version = '1.1'

    def __init__(self):
        super(LightRigManager, self).__init__()

    def custom_ui(self):
        super(LightRigManager, self).custom_ui()

        self.set_logo('solstice_lightrigs_logo')
        self.set_info_url('https://tpoveda.github.io/solstice/solsticepipeline/solsticetools/solsticelightrigmanager/')

        self.resize(100, 150)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        self.main_layout.addLayout(buttons_layout)

        open_btn = QToolButton()
        open_btn.setIcon(resource.icon('open'))
        sync_btn = QToolButton()
        sync_btn.setIcon(resource.icon('sync'))
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(splitters.get_horizontal_separator_widget())
        buttons_layout.addWidget(sync_btn)
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addLayout(splitters.SplitterLayout())

        self.light_rigs_layout = QHBoxLayout()
        self.light_rigs_layout.setContentsMargins(5, 5, 5, 5)
        self.light_rigs_layout.setSpacing(5)
        self.light_rigs_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.light_rigs_layout)

        self._update_ui()

        open_btn.clicked.connect(self._on_open_light_rigs_folder)
        sync_btn.clicked.connect(self._on_sync_light_rigs)

    @staticmethod
    def get_solstice_light_rigs_path(sync=False):
        """
        Returns Solstice Light Rigs path
        :return: str
        """

        light_rigs_path = os.path.join(sp.get_solstice_assets_path(), 'lighting', 'Light Rigs')
        if sync:
            syncdialog.SolsticeSyncPath(paths=[light_rigs_path]).sync()
        if os.path.exists(light_rigs_path):
            sys.solstice.logger.debug('Getting Light Rigs Path: {0}'.format(light_rigs_path))
            return light_rigs_path
        else:
            sys.solstice.logger.error('Impossible to sync light rigs! Please contact TD!')
            return None

    def _update_ui(self):
        valid_light_rigs = self.get_solstice_light_rigs_path()
        if not valid_light_rigs:
            return
        working_path = os.path.join(valid_light_rigs, '__working__')
        if not os.path.exists(working_path):
            return

        qtutils.clear_layout_widgets(self.light_rigs_layout)
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
            sys.solstice.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, o=True, f=True)

    @staticmethod
    def import_light_rig(name):
        # if cmds.file(query=True, modified=True):
        #     cmds.SaveScene()

        light_rigs_path = LightRigManager.get_solstice_light_rigs_path(sync=False)
        light_rig = os.path.join(light_rigs_path, '__working__', name.title(), 'LR_{}.ma'.format(name.title()).replace(' ', '_'))
        if not os.path.exists(light_rig):
            sys.solstice.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, i=True, f=True)

    @staticmethod
    def reference_light_rig(name, do_save=True):
        # if do_save:
        #     if cmds.file(query=True, modified=True):
        #         cmds.SaveScene()

        light_rigs_path = LightRigManager.get_solstice_light_rigs_path(sync=False)
        light_rig = os.path.join(light_rigs_path, '__working__', name.title(),
                                 'LR_{}.ma'.format(name.title()).replace(' ', '_'))
        if not os.path.exists(light_rig):
            sys.solstice.logger.error('Light Rig File {} does not exists!'.format(light_rig))
            return False

        cmds.file(light_rig, reference=True, f=True)

    def _on_open_light_rigs_folder(self):
        light_rigs_path = os.path.join(self.get_solstice_light_rigs_path(sync=False), '__working__')
        if os.path.exists(light_rigs_path):
            pythonutils.open_folder(light_rigs_path)

    def _on_sync_light_rigs(self):
        self.get_solstice_light_rigs_path(sync=True)
        self._update_ui()


def run():
    LightRigManager().show()
