#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_autoUpdater.py
# by Tomás Poveda
# ______________________________________________________________________
# Auto Updater script for solstice_tools
# ______________________________________________________________________
# ==================================================================="""

from solstice_tools.scripts.solstice_config import solstice_update_utils as utils

import maya.utils as mutils

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def updateTools(ui=False, stopAtEnd=False):

    if ui:
        import solstice_updater_ui
        reload(solstice_updater_ui)
        solstice_updater_ui.initUI()
        return

    utils.updateTools()
    if stopAtEnd:
        input('solstice_tools setup is finished! Press a key to continue ...')

if __name__ == '__main__':
    updateTools()