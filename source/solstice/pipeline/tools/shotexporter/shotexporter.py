#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to export shot files to be used in the shot builder tool
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

from artellapipe.gui import window


class ShotExporter(window.ArtellaWindow, object):

    LOGO_NAME = 'manager_logo'

    def __init__(self, project):
        super(ShotExporter, self).__init__(
            project=project,
            name='ShotExporter',
            title='Shot Exporter',
            size=(550, 650)
        )

    def ui(self):
        super(ShotExporter, self).ui()

        self._tab = ShotExporterTab()

        self.main_layout.addWidget(self._tab)


class ShotExporterTab(QTabWidget, object):
    def __init__(self, parent=None):
        super(ShotExporterTab, self).__init__(parent)


def run(project):
    win = ShotExporter(project=project)
    win.show()

    return win
