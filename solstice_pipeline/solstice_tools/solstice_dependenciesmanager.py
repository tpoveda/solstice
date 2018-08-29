#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_dependenciesmanager.py
# by Tomas Poveda
# Tool to manage asset and sequences dependencies
# ______________________________________________________________________
# ==================================================================="""

import sys

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows


class DependenciesManager(solstice_windows.Window, object):

    name = 'SolsticeDependencies'
    title = 'Solstice Tools - Dependencies Manager'
    version = '1.0'

    def __init__(self):
        super(DependenciesManager, self).__init__()

    def custom_ui(self):
        super(DependenciesManager, self).custom_ui()

        self.set_logo('solstice_dependenciesmanager_logo')

def run():
    win = DependenciesManager.show()
