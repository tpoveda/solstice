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

from Qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_sync_dialog
from solstice_utils import solstice_qt_utils


class LightRigManager(solstice_windows.Window, object):

    title = 'Solstice Tools - Light Rigs'
    version = '1.0'
    docked = False

    def __init__(self, name='LightRigWindow', parent=None, **kwargs):
        super(LightRigManager, self).__init__(parent=parent)

    def custom_ui(self):
        super(LightRigManager, self).custom_ui()

        self.set_logo('solstice_lightrigs_logo')

        self.get_solstice_light_rigs_path()

    @classmethod
    def get_solstice_light_rigs_path(cls, ask_sync=True):
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
                result = solstice_qt_utils.show_question(None, 'Files are not syncrhonized', 'Do you want to synchronize Light Rigs files?')
                if result == QMessageBox.Yes:
                    sync_dlg = solstice_sync_dialog.SolsticeSyncPath(paths=[light_rigs_path]).sync()
                    cls.get_solstice_light_rigs_path(ask_sync=False)

        return None


def run():
    reload(solstice_sync_dialog)
    reload(solstice_qt_utils)
    LightRigManager.run()