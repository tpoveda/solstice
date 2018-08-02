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

from solstice_qt.QtWidgets import *
from solstice_qt.QtCore import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_sync_dialog
from solstice_utils import solstice_qt_utils


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


class LightRigManager(solstice_windows.Window, object):

    name = 'Solstice_LightRigs'
    title = 'Solstice Tools - Light Rigs Manager'
    version = '1.0'
    docked = False

    def __init__(self, name='LightRigWindow', parent=None, **kwargs):
        super(LightRigManager, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(LightRigManager, self).custom_ui()

        self.set_logo('solstice_lightrigs_logo')

        self.light_rigs_layout = QHBoxLayout()
        self.light_rigs_layout.setContentsMargins(5, 5, 5, 5)
        self.light_rigs_layout.setSpacing(5)
        self.light_rigs_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.light_rigs_layout)

        self._update_ui()

    @classmethod
    def get_solstice_light_rigs_path(cls, ask_sync=False):
        """
        Returns Solstice Light Rigs path
        :return: str
        """

        light_rigs_path = os.path.join(sp.get_solstice_assets_path(), 'lighting', 'Light Rigs')
        if os.path.exists(light_rigs_path):
            sp.logger.debug('Getting Light Rigs Path: {0}'.format(light_rigs_path))
            return light_rigs_path
        else:
            if ask_sync:
                result = solstice_qt_utils.show_question(None, 'Light Rigs are not syncrhonized', 'Do you want to synchronize Light Rigs files?')
                if result == QMessageBox.No:
                    return None
            solstice_sync_dialog.SolsticeSyncPath(paths=[light_rigs_path]).sync()
            cls.get_solstice_light_rigs_path(ask_sync=False)

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


def run():
    reload(solstice_sync_dialog)
    reload(solstice_qt_utils)
    LightRigManager.run()