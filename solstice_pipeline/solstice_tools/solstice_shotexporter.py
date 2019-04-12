#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shotexporter.py
# by Tomas Poveda
# Tool to export shot elements
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

from solstice_pipeline.solstice_gui import solstice_windows, solstice_splitters


class LayoutExporter(QWidget, object):
    def __init__(self, parent=None):
        super(LayoutExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


class AnimationExporter(QWidget, object):
    def __init__(self, parent=None):
        super(AnimationExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


class FXExporter(QWidget, object):
    def __init__(self, parent=None):
        super(FXExporter, self).__init__(parent=parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


class ShotExporter(solstice_windows.Window, object):
    name = 'SolsticeShotExporter'
    title = 'Solstice Tools - Shot Exporter'
    version = '1.0'

    def __init__(self):
        super(ShotExporter, self).__init__()

    def custom_ui(self):
        super(ShotExporter, self).custom_ui()

        # self.set_logo('solstice_standinmanager_logo')

        self.resize(550, 650)

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.layout_exporter = LayoutExporter()
        self.anim_exporter = AnimationExporter()
        self.fx_exporter = AnimationExporter()

        self.main_tabs.addTab(self.layout_exporter, 'Layout')
        self.main_tabs.addTab(self.anim_exporter, 'Animation')
        self.main_tabs.addTab(self.fx_exporter, 'FX')

    #     self.main_tabs.currentChanged.connect(self._on_change_tab)
    #
    # def _on_change_tab(self, tab_index):
    #     if tab_index == 1:
    #         self.alembic_exporter.refresh()




def run():
    win = ShotExporter().show()
    return win
