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

from solstice_qt.QtWidgets import *
from solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows


class DependenciesManager(solstice_windows.Window, object):

    name = 'Solstice_Dependencies'
    title = 'Solstice Tools - Dependencies Manager'
    version = '1.0'
    dock = False

    def __init__(self, name='DependenciesWindow', parent=None, **kwargs):
        super(DependenciesManager, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(DependenciesManager, self).custom_ui()

        self.set_logo('solstice_dependenciesmanager_logo')

def run():
    DependenciesManager.run()
