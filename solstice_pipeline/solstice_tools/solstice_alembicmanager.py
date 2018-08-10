#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_alembicmanager.py
# by Tomas Poveda
# Tool to export/import Alembic (.abc) files
# ______________________________________________________________________
# ==================================================================="""

import sys

from solstice_qt.QtWidgets import *
from solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows, solstice_accordion
from solstice_pipeline.resources import solstice_resource


class AlembicImporter(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicImporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)


class AlembicExporter(QWidget, object):
    def __init__(self, parent=None):
        super(AlembicExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        export_tag_layout = QHBoxLayout()
        export_tag_lbl = QLabel('      Export Tag: ')
        self.export_tag = QComboBox()
        self.export_tag.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        export_tag_layout.addWidget(export_tag_lbl)
        export_tag_layout.addWidget(self.export_tag)

        frame_range_layout = QHBoxLayout()
        frame_range_layout.setContentsMargins(2, 2, 2, 2)
        frame_range_layout.setSpacing(2)
        frame_range_lbl = QLabel('Frame Range:  ')
        self.start = QSpinBox()
        self.start.setRange(-sys.maxint, sys.maxint)
        self.start.setFixedHeight(20)
        self.start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.end = QSpinBox()
        self.end.setRange(-sys.maxint, sys.maxint)
        self.end.setFixedHeight(20)
        self.end.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for widget in [frame_range_lbl, self.start, self.end]:
            frame_range_layout.addWidget(widget)

        folder_icon = solstice_resource.icon('open')
        export_path_layout = QHBoxLayout()
        export_path_layout.setContentsMargins(2, 2, 2, 2)
        export_path_layout.setSpacing(2)
        export_path_label = QLabel('  Export Path: ')
        self.export_path_line = QLineEdit()
        self.export_path_line.setReadOnly(True)
        self.export_path_btn = QPushButton()
        self.export_path_btn.setIcon(folder_icon)
        self.export_path_btn.setIconSize(QSize(18, 18))
        self.export_path_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        export_path_layout.addWidget(export_path_label)
        export_path_layout.addWidget(self.export_path_line)
        export_path_layout.addWidget(self.export_path_btn)

        self.main_layout.addLayout(export_tag_layout)
        self.main_layout.addLayout(frame_range_layout)
        self.main_layout.addLayout(export_path_layout)

    def export(self, nodes, filename, start_frame=1, end_frame=24):
        pass


class AlembicManager(solstice_windows.Window, object):
    name = 'Solstice_AlembicManager'
    title = 'Solstice Tools - Alembic Manager'
    version = '1.0'

    def __init__(self):
        super(AlembicManager, self).__init__()

    def custom_ui(self):
        super(AlembicManager, self).custom_ui()

        self.set_logo('solstice_alembicmanager_logo')

        self.main_widget = solstice_accordion.AccordionWidget(parent=self)
        self.main_widget.rollout_style = solstice_accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.main_widget)

        alembic_importer = AlembicImporter()
        alembic_exporter = AlembicExporter()
        self.main_widget.add_item('Importer', alembic_importer, collapsed=False)
        self.main_widget.add_item('Exporter', alembic_exporter, collapsed=False)


def run():
    win = AlembicManager().show()
