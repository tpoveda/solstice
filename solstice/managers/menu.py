#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains manager that handles Solstice DCC Menu
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import webbrowser

from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.python import decorators
from tpDcc.libs.qt.core import qtutils

import artellapipe
import artellapipe.register
from artellapipe.managers import menus
import artellapipe.libs.kitsu as kitsu_lib


class SolsticeMenu(menus.ArtellaMenusManager, object):
    def __init__(self):

        super(SolsticeMenu, self).__init__()

    def create_menus(self, package_name, project):
        valid_creation = super(SolsticeMenu, self).create_menus(package_name=package_name, project=project)
        if not valid_creation:
            artellapipe.logger.warning('Something went wrong during the creation of SolsticeMenu Menu')
            return False

        return self.create_kitsu_menu()

    def create_kitsu_menu(self):

        parent_menu_bar = qtutils.get_window_menu_bar(tpDcc.Dcc.get_main_window())
        if not parent_menu_bar:
            return

        kitsu_menu_name = 'kitsu_menu'

        # Remove previous created menu
        for child_widget in parent_menu_bar.children():
            if child_widget.objectName() == kitsu_menu_name:
                child_widget.deleteLater()

        self._kitsu_action = QAction(self._parent.menuBar())
        self._kitsu_action.setIcon(tpDcc.ResourcesMgr().icon('kitsu'))
        self._parent.menuBar().addAction(self._kitsu_action)
        self._kitsu_action.setObjectName(kitsu_menu_name)
        self._kitsu_action.triggered.connect(self._on_kitsu_open)

        return True

    def _on_kitsu_open(self):
        """
        Internal callback function that is called when kitsu action is pressed
        """

        project_url = kitsu_lib.config.get('project_url', None)
        if not project_url:
            return None

        webbrowser.open(project_url)


@decorators.Singleton
class SolsticeMenuManagerSingleton(SolsticeMenu, object):
    def __init__(self):
        SolsticeMenu.__init__(self)


artellapipe.register.register_class('MenusMgr', SolsticeMenuManagerSingleton)
