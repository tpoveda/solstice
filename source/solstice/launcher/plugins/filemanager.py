#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains File Manager Artella Launcher Plugin implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

from artellalauncher.core import plugin
from artellapipe.tools.artellamanager.widgets import localsync, serversync


class FileManagerPlugin(plugin.ArtellaLauncherPlugin, object):

    LABEL = 'File Manager'
    ORDER = 1
    ICON = 'hard_drive'

    def __init__(self, project, parent=None):
        super(FileManagerPlugin, self).__init__(project=project, parent=parent)

    def ui(self):
        super(FileManagerPlugin, self).ui()

        local_sync = localsync.ArtellaPathSyncWidget(project=self._project)
        self.main_layout.addWidget(local_sync)


class ArtellaFileManager(plugin.ArtellaLauncherPlugin, object):

    LABEL = 'Artella Manager'
    ORDER = 2
    ICON = 'artella'

    def __init__(self, project, parent=None):
        super(ArtellaFileManager, self).__init__(project=project, parent=parent)

    def ui(self):
        super(ArtellaFileManager, self).ui()

        server_sync = serversync.ArtellaSyncWidget(project=self._project)
        self.main_layout.addWidget(server_sync)