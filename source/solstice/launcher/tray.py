#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Artella tray
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.gui import tray

from Qt.QtWidgets import *

import solstice


class SolsticeTray(tray.ArtellaTray, object):
    def __init__(self, project, parent=None):
        super(SolsticeTray, self).__init__(project=project, parent=parent)

    def create_menu(self):
        menu = QMenu(self)

        project_name = self._project.name.title()

        documentation_icon = solstice.resource.icon('documentation')
        project_icon = solstice.resource.icon('solstice', theme=None)
        artella_icon = solstice.resource.icon('artella')
        email_icon = solstice.resource.icon('message')
        kitsu_icon = solstice.resource.icon('kitsu')
        drive_icon = solstice.resource.icon('drive')

        doc_action = QAction(documentation_icon, '{} Documentation'.format(project_name), self, statusTip='Open {} Tools Documentation webpage'.format(project_name), triggered=self._on_open_documentation)
        web_action = QAction(project_icon, '{} Web'.format(project_name), self, statusTip='Open {} Project webpage'.format(project_name), triggered=self._on_open_webpage)
        artella_action = QAction(artella_icon, '{} Artella Project'.format(project_name), self, statusTip='Open {} Artella Project webpage'.format(project_name), triggered=self._on_open_artella_project)
        email_action = QAction(email_icon, 'Send Email', self, statusTip='Send Email to {} TD team'.format(project_name), triggered=self._on_send_email)
        kitsu_action = QAction(kitsu_icon, '{} Kitsu webpage'.format(project_name), self, statusTip='Open {} Kitsu webpage'.format(project_name), triggered=self._on_open_kitsu)
        drive_action = QAction(drive_icon, '{} Drive webpage'.format(project_name), self, statusTip='Open {} Drive webpage'.format(project_name), triggered=self._on_open_drive)
        for action in [doc_action, web_action, artella_action, email_action, kitsu_action, drive_action]:
            menu.addAction(action)

        return menu

    def _on_open_documentation(self):
        self.project.open_documentation()

    def _on_open_webpage(self):
        self.project.open_webpage()

    def _on_open_artella_project(self):
        self.project.open_artella_project_url()

    def _on_send_email(self):
        self.project.send_email()

    def _on_open_kitsu(self):
        self.project.open_kitsu()

    def _on_open_drive(self):
        self.project.open_drive()
