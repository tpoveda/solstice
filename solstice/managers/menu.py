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

import logging
import webbrowser

from Qt.QtWidgets import *

from tpPyUtils import decorators

import artellapipe.register
from artellapipe.utils import resource
import artellapipe.libs.kitsu as kitsu_lib

LOGGER = logging.getLogger()


class SolsticeMenu(artellapipe.Menu, object):
    def __init__(self):

        self._kitsu_action_object_name = None

        super(SolsticeMenu, self).__init__()

    def set_project(self, project):
        self._kitsu_action_object_name = '{}_kitsu'.format(self._menu_name)
        super(SolsticeMenu, self).set_project(project)

    def create_menus(self):
        valid_creation = super(SolsticeMenu, self).create_menus()
        if not valid_creation:
            LOGGER.warning('Something went wrong during the creation of SolsticeMenu Menu')
            return False

        return self.create_kitsu_menu()

    def get_menu_names(self):
        menu_names = super(SolsticeMenu, self).get_menu_names()
        if self._kitsu_action_object_name not in menu_names:
            menu_names.append(self._kitsu_action_object_name)

        return menu_names

    def create_kitsu_menu(self):
        self._kitsu_action = QAction(self._parent.menuBar())
        self._kitsu_action.setIcon(resource.ResourceManager().icon('kitsu'))
        self._parent.menuBar().addAction(self._kitsu_action)
        self._kitsu_action.setObjectName(self._kitsu_action_object_name)
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


artellapipe.register.register_class('MenuMgr', SolsticeMenuManagerSingleton)
