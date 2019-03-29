#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_menu.py
# by Tomas Poveda
# Module that contains base class to create Solstice Menu
# ______________________________________________________________________
# ==================================================================="""

import os
import json
from collections import OrderedDict

import solstice_pipeline as sp

if sp.dcc == sp.SolsticeDCC.Maya:
    import maya.cmds as cmds
    from solstice_utils import solstice_maya_utils as utils


class SolsticeMenu(object):
    def __init__(self, name='Solstice'):
        super(SolsticeMenu, self).__init__()

        self.name = name

    def create_menu(self, file_path=None, parent_menu=None):
        """
        Creates a new DCC menu app
        If file path is not given the menu is created without items
        :param name: str, name for the menu
        :param file_path: str, path where JSON menu file is located
        :param parent_menu: str, Name of the menu to append this menu to
        :return: variant, nativeMenu || None
        """

        if utils.check_menu_exists(self.name):
            return

        menu_created = False

        if parent_menu:
            m = utils.find_menu(parent_menu)
            if m:
                self._native_pointer = cmds.menuItem(subMenu=True, parent=m, tearOff=True, label=self.name)
                menu_created = True

        s_menu = None
        if not menu_created:
            s_menu = cmds.menu(parent=utils.main_menu(), tearOff=True, label=self.name)

        if not file_path or not s_menu:
            return

        if not os.path.isfile(file_path):
            sp.logger.warning('Menu was not created because menu file is not valid or does not exists!')
            return

        menu_data = None
        with open(file_path, 'r') as f:
            menu_data = json.load(f, object_pairs_hook=OrderedDict)

        if menu_data:
            menu_categories = list(menu_data.keys())
            for category in menu_categories:
                self.create_category(category_name=category, category_items=menu_data[category], parent_menu=s_menu)

    @staticmethod
    def create_category(category_name, category_items, parent_menu):
        """
        Creates a new category on the passed menu. If not menu specified this menu is used, if exists
        :param parent_menu: str, menu to add category to
        :param category_name: str, name of the category
        :param category_items: list<str>, list of items to add to the category
        :return: variant, nativeMenu || None
        """

        submenu = cmds.menuItem(subMenu=True, tearOff=True, parent=parent_menu, label=category_name)
        for item in category_items:
            cmds.menuItem(parent=submenu, label=item['label'], command=item['command'])
