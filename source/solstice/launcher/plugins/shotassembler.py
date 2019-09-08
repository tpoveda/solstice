#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Shot Assembler Plugin implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

from artellalauncher.core import plugin


class ShotAssemblerPlugin(plugin.ArtellaLauncherPlugin, object):

    LABEL = 'Shot Assembler'
    ORDER = 3
    ICON = 'assembler'

    def __init__(self, project, parent=None):
        super(ShotAssemblerPlugin, self).__init__(project=project, parent=parent)

    def ui(self):
        super(ShotAssemblerPlugin, self).ui()

        self.main_layout.addWidget(QPushButton('File Manager'))
