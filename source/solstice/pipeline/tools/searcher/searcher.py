#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
# ==================================================================="""


import sys

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *
from pipeline.externals.solstice_qt.QtGui import *

import pipeline as sp

if sp.is_maya():
    import maya.cmds as cmds
    from pipeline.utils import mayautils as utils


class SolsticeSearcher():

    @staticmethod
    def install_hotkeys():
        """
        This function updates hotkeys related with Solstice Tools
        """

        system = sys.platform

        if sp.is_maya():
            maya_version = cmds.about(version=True)
            hotkey = ''
            if '2014' in maya_version:
                cmds.nameCommand('solsticeSearcherCommand', annotation='Launch Solstice Searcher',
                                 command='python("from solstice_pipeline.solstice_tools import solstice_searcher; solstice_searcher.run()")')
                cmds.hotkey(k='Tab', ctl=True, name='solsticeSearcherCommand')
                sp.logger.debug('Solstice Searcher loaded successfully.\n 2014 Hotkey installed on: {}'.format(hotkey))
            else:
                main_win = utils.get_maya_window()
                searcher_action = QAction(main_win)

                def solstice_searcher_tab():
                    cmds.evalDeferred('from solstice_pipeline.solstice_tools import solstice_searcher; solstice_searcher.run()')

                if system == 'darwin':
                    hotkey = 'SHIFT + TAB'
                    searcher_action.setShortcut(QKeySequence(Qt.SHIFT + Qt.Key_Tab))
                else:
                    hotkey = 'CTRL + TAB'
                    searcher_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Tab))

                searcher_action.setShortcutContext(Qt.ApplicationShortcut)
                searcher_action.triggered.connect(solstice_searcher_tab)
                main_win.addAction(searcher_action)
                sp.logger.debug('Solstice Searcher loaded successfully! \n Hotkey installed on: {}'.format(hotkey))

            return hotkey
        else:
            sp.logger.warning('Impossible to install searcher hotkey in DCC: {}'.format(sp.dcc))

    @staticmethod
    def get_content():
        searcher_command_list = list()
        searcher_icons_list = list()
        searcher_categories = list()
        searcher_actions_list = list()

        action_count = 0


def run():
    print('Come on!')
