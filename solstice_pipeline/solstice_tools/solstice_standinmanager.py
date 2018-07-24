#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_standinmanager.py
# by Tomas Poveda
# Tool to export/import Arnold Standin (.ass) files
# ______________________________________________________________________
# ==================================================================="""

import sys

from solstice_qt.QtWidgets import *
from solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows, solstice_accordion
from solstice_pipeline.resources import solstice_resource


class StandinImporter(QWidget, object):
    def __init__(self, parent=None):
        super(StandinImporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)


class StandinExporter(QWidget, object):
    def __init__(self, parent=None):
        super(StandinExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)


class StandinManager(solstice_windows.Window, object):
    name = 'Solstice_StandinManager'
    title = 'Solstice Tools - Standin Manager'
    version = '1.0'
    docked = True

    def __init__(self, name='StandinManagerWindow', parent=None):
        super(StandinManager, self).__init__(name=name, parent=parent)

    def custom_ui(self):
        super(StandinManager, self).custom_ui()

        self.set_logo('solstice_standinmanager_logo')

        self.main_widget = solstice_accordion.AccordionWidget(parent=self)
        self.main_widget.rollout_style = solstice_accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.main_widget)

        alembic_importer = StandinImporter()
        alembic_exporter = StandinExporter()
        self.main_widget.add_item('Importer', alembic_importer, collapsed=False)
        self.main_widget.add_item('Exporter', alembic_exporter, collapsed=False)


def run():
    StandinManager.run()
