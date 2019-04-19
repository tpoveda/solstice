#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to export shot elements
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import base, window

from solstice.pipeline.tools.shotexporter.export.layout import exporter as layout_exporter
from solstice.pipeline.tools.shotexporter.export.animation import exporter as anim_exporter
# from solstice.pipeline.tools.shotexporter.export.fx import exporter as fx_exporter
# from solstice.pipeline.tools.shotexporter.export.lighting import exporter as light_exporter
# from solstice.pipeline.tools.shotexporter.export.camera import exporter as cam_exporter

reload(layout_exporter)
reload(anim_exporter)

class ShotExporter(window.Window, object):
    name = 'SolsticeShotExporter'
    title = 'Solstice Tools - Shot Exporter'
    version = '1.0'

    def __init__(self):
        super(ShotExporter, self).__init__()

    def custom_ui(self):
        super(ShotExporter, self).custom_ui()

        # self.set_logo('solstice_standinmanager_logo')
        self.resize(550, 650)

        self.export_widget = ShotExportWidget()
        self.main_layout.addWidget(self.export_widget)


class ShotExportWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(ShotExportWidget, self).__init__(parent=parent)

    def custom_ui(self):
        super(ShotExportWidget, self).custom_ui()

        self.main_tabs = QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.layout_exporter = layout_exporter.LayoutExporter()
        self.anim_exporter = anim_exporter.AnimationExporter()
    #     self.fx_exporter = fx_exporter.FXExporter()
    #     self.light_exporter = light_exporter.LightingExporter()
    #     self.cameras_exporter = cam_exporter.CamerasExporter()
    #
        self.main_tabs.addTab(self.layout_exporter, 'Layout')
        self.main_tabs.addTab(self.anim_exporter, 'Animation')
    #     self.main_tabs.addTab(self.fx_exporter, 'FX')
    #     self.main_tabs.addTab(self.light_exporter, 'Lighting')
    #     self.main_tabs.addTab(self.cameras_exporter, 'Cameras')
    #
    #     self.layout_exporter.init_ui()
    #
        self.main_tabs.currentChanged.connect(self._on_change_tab)
    #
    def _on_change_tab(self, tab_index):
        if tab_index == 0:
            self.layout_exporter.refresh()
        if tab_index == 1:
            self.anim_exporter.refresh()
    #     if tab_index == 2:
    #         self.fx_exporter.refresh()
    #     elif tab_index == 3:
    #         self.light_exporter.refresh()
    #     elif tab_index == 4:
    #         self.cameras_exporter.refresh()

def run():
    win = ShotExporter().show()
    return win
