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

try:
    from solstice_config import solstice_update_utils as utils
except:
    from solstice_tools.scripts.solstice_config import solstice_update_utils as utils

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def updateTools(ui=False, stopAtEnd=False, progress_bar=None):

    if ui:
        import solstice_updater_ui
        reload(solstice_updater_ui)
        solstice_updater_ui.initUI()
        return

    utils.updateTools(progress_bar=progress_bar)
    if stopAtEnd:
        input('solstice_tools setup is finished! Press a key to continue ...')

if __name__ == '__main__':
    updateTools()