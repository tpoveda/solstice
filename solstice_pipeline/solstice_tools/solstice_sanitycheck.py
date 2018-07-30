#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sanitycheck.py
# by Tomas Poveda @ Original version by Irakli Kublashvili
# Solstice Pipeline tool to smooth the workflow between Maya and Artella
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtWidgets import *

from solstice_pipeline.solstice_utils import solstice_maya_utils
from solstice_pipeline.solstice_gui import solstice_windows

from solstice_checks import solstice_checkgroups


class SanityCheck(solstice_windows.Window, object):

    name = 'Solstice_SanityCheck'
    title = 'Solstice Tools - Sanity Check'
    version = '1.0'
    dock = False

    def __init__(self, name='SanityCheckWindow', parent=None, **kwargs):
        super(SanityCheck, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SanityCheck, self).custom_ui()

        self.set_logo('solstice_sanitycheck_logo')

        self.checks_tab = QTabWidget()
        self.main_layout.addWidget(self.checks_tab)

        # =============================================================================

        self.add_sanity_group(solstice_checkgroups.GeneralSanityCheck())
        self.add_sanity_group(solstice_checkgroups.ShadingSanityCheck())

    def add_sanity_group(self, sanity_group):
        self.checks_tab.addTab(sanity_group, sanity_group.name)


def run():
    reload(solstice_maya_utils)
    SanityCheck.run()
