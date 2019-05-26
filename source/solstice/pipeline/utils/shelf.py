#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class to create Solstice Shelf
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import json
from collections import OrderedDict
from functools import partial

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.utils import qtutils as qt
from solstice.pipeline.resources import resource

if sp.is_houdini():
    from solstice.pipeline.utils import houdiniutils


class SolsticeShelf(object):
    def __init__(self, name='Solstice', label_background=(0, 0, 0, 0), label_color=(0.9, 0.9, 0.9)):
        super(SolsticeShelf, self).__init__()

        self.name = name
        self.label_background = label_background
        self.label_color = label_color

        self.category_btn = None
        self.category_menu = None

    @staticmethod
    def add_menu_item(parent, label, command='', icon=''):
        """
        Adds a menu item with the given attributes
        :param parent:
        :param label:
        :param command:
        :param icon:
        :return:
        """

        return sys.solstice.dcc.add_shelf_menu_item(parent=parent, label=label, command=command, icon=icon)

    @staticmethod
    def add_sub_menu(parent, label, icon=None):
        """
        Adds a sub menu item with the given label and icon to the given parent popup menu
        :param parent:
        :param label:
        :param icon:
        :return:
        """

        return sys.solstice.dcc.add_shelf_sub_menu_item(parent=parent, label=label, icon=icon)

    def create(self, delete_if_exists=True):
        """
        Creates a new shelf
        """

        if delete_if_exists:
            if sp.is_houdini():
                from solstice.pipeline.utils import houdiniutils
                if houdiniutils.shelf_set_exists(shelf_set_name=self.name):
                    houdiniutils.remove_shelf_set(name=self.name)
            else:
                if sys.solstice.dcc.shelf_exists(shelf_name=self.name):
                    sys.solstice.dcc.delete_shelf(shelf_name=self.name)
        else:
            if sp.is_houdini():
                from solstice.pipeline.utils import houdiniutils
                assert not houdiniutils.shelf_set_exists(shelf_set_name=self.name), 'Shelf Set with name {} already exists!'.format(self.name)
            else:
                assert not sys.solstice.dcc.shelf_exists(self.name), 'Shelf with name {} already exists!'.format(self.name)

        if sp.is_houdini():
            houdiniutils.create_shelf_set(name=self.name, dock=True)
        else:
            self.name = sys.solstice.dcc.create_shelf(shelf_name=self.name)

        # ========================================================================================================

        if sp.is_maya():
            import maya.OpenMayaUI as OpenMayaUI
            self.category_btn = QPushButton('')
            self.category_btn.setIcon(resource.icon('solstice_s'))
            self.category_btn.setIconSize(QSize(18, 18))
            self.category_menu = QMenu(self.category_btn)
            self.category_btn.setStyleSheet('QPushButton::menu-indicator {image: url(myindicator.png);subcontrol-position: right center;subcontrol-origin: padding;left: -2px;}')
            self.category_btn.setMenu(self.category_menu)
            self.category_lbl = QLabel('MAIN')
            self.category_lbl.setAlignment(Qt.AlignCenter)
            font = self.category_lbl.font()
            font.setPointSize(6)
            self.category_lbl.setFont(font)
            menu_ptr = OpenMayaUI.MQtUtil.findControl(self.name)
            menu_widget = qt.wrapinstance(menu_ptr, QWidget)
            menu_widget.layout().addWidget(self.category_btn)
            menu_widget.layout().addWidget(self.category_lbl)

            self.add_separator()

    def set_as_active(self):
        """
        Sets this shelf as active shelf in current DCC session
        """

        if sp.is_maya():
            import maya.cmds as cmds
            import maya.mel as mel
            main_shelf = mel.eval("$_tempVar = $gShelfTopLevel")
            cmds.tabLayout(main_shelf, edit=True, selectTab=self.name)

    def add_button(self, label, tooltip=None, icon='customIcon.png', command=None, double_command=None, command_type='python'):
        """
        Adds a shelf button width the given parameters
        :param label:
        :param tooltip:
        :param icon:
        :param command:
        :param double_command:
        :param command_type:
        :return:
        """

        if sp.is_houdini():
            return houdiniutils.create_shelf_tool(
                tool_name='solstice_{}'.format(label),
                tool_label=label,
                tool_type=command_type,
                tool_script=command,
                icon=icon
            )
        else:
            import maya.cmds as cmds
            cmds.setParent(self.name)
            command = command or ''
            double_command = double_command or ''
            return cmds.shelfButton(width=37, height=37, image=icon or '', label=label, command=command,
                                    doubleClickCommand=double_command, annotation=tooltip or '', imageOverlayLabel=label,
                                    overlayLabelBackColor=self.label_background, overlayLabelColor=self.label_color,
                                    sourceType=command_type)

    def add_separator(self):
        """
        Adds a separator to shelf
        :param parent:
        :return:
        """

        return sys.solstice.dcc.add_shelf_separator(shelf_name=self.name)

    def build_category(self, shelf_file, category_name):
        if sp.is_maya():
            self.category_lbl.setText(category_name.upper())
            self.load_category(shelf_file, 'general', clear=True)
            if category_name != 'general':
                self.add_separator()
                self.load_category(shelf_file, category_name, clear=False)

    def build_categories(self, shelf_file, categories):
        """
        Builds all categories given
        :param categories: list<str>, list of categories to build
        """

        if sp.is_houdini():
            all_shelves = list()
            for cat in categories:
                shelf_name = 'solstice_{}'.format(cat)
                if houdiniutils.shelf_exists(shelf_name=shelf_name):
                    houdiniutils.remove_shelf(name=shelf_name)
                if not houdiniutils.shelf_exists(shelf_name=shelf_name):
                    new_shelve = houdiniutils.create_shelf(shelf_name=shelf_name, shelf_label=cat.title())
                    all_shelves.append(new_shelve)
            shelf_set = houdiniutils.get_shelf_set(shelf_set_name=self.name)
            if shelf_set and all_shelves:
                all_shelves.reverse()
                shelf_set.setShelves(all_shelves)
        else:
            self.category_lbl.setText('ALL')

            self.load_category(shelf_file, 'general', clear=True)
            for cat in categories:
                if cat == 'general':
                    continue
                self.add_separator()
                self.load_category(shelf_file, cat, clear=False)

    def load_category(self, shelf_file, category_name, clear=True):
        """
        Loads into a shelf all the items of given category name, if exists
        :param category_name: str, name of the category
        """

        if clear:
            self.clear_list()

        with open(shelf_file) as f:
            shelf_data = json.load(f, object_pairs_hook=OrderedDict)
            if not 'solstice_shelf' in shelf_data:
                sys.solstice.logger.warning('Impossible to create Solstice Shelf! Please contact TD!')
                return

            if sp.is_houdini():
                for item, item_data in shelf_data['solstice_shelf'].items():
                    if item != category_name:
                        continue
                    all_tools = list()
                    for i in item_data:
                        annotation = i.get('annotation')
                        if annotation == 'separator':
                            continue
                        dcc = i.get('dcc')
                        if sys.solstice.dcc.get_name() not in dcc:
                            continue
                        icon = os.path.join(sp.get_solstice_icons_path(), i.get('icon'))
                        command = i.get('command')
                        label = i.get('label')
                        new_tool = self.add_button(label=label, command=command, icon=icon, tooltip=annotation)
                        if new_tool:
                            all_tools.append(new_tool)
                    current_shelf = houdiniutils.get_shelf(shelf_name='solstice_{}'.format(item))
                    if current_shelf and all_tools:
                        current_shelf.setTools(all_tools)
            else:
                for item, item_data in shelf_data['solstice_shelf'].items():
                    if item != category_name:
                        continue

                    for i in item_data:
                        annotation = i.get('annotation')
                        if annotation == 'separator':
                            self.add_separator()
                            continue

                        dcc = i.get('dcc')
                        if sys.solstice.dcc.get_name() not in dcc:
                            continue
                        icon = i.get('icon')
                        command = i.get('command')
                        # NOTE: In Maya we do not want labels, we force an empty string
                        label = ''
                        # label = i.get('label')
                        self.add_button(label=label, command=command, icon=icon, tooltip=annotation)
                    return

    def build(self, shelf_file):
        """
        Builds shelf from JSON file
        :param shelf_file: str
        """

        first_item = None

        all_categories = list()

        with open(shelf_file) as f:
            shelf_data = json.load(f, object_pairs_hook=OrderedDict)
            if not 'solstice_shelf' in shelf_data:
                sys.solstice.logger.warning('Impossible to create Solstice Shelf! Please contact TD!')
                return

            if sp.is_houdini():
                self.build_categories(shelf_file=shelf_file, categories=shelf_data['solstice_shelf'].keys())
                for i, item in enumerate(shelf_data['solstice_shelf'].keys()):
                    self.load_category(shelf_file, item, clear=False)
            else:
                for i, item in enumerate(shelf_data['solstice_shelf'].keys()):
                    if i == 0:
                        first_item = item

                    category_action = self.category_menu.addAction(item.title())
                    category_action.triggered.connect(partial(self.build_category, shelf_file, item))
                    all_categories.append(item)
                category_action = self.category_menu.addAction('All')
                category_action.triggered.connect(partial(self.build_categories, shelf_file, all_categories))

                if first_item:
                    self.load_category(shelf_file, first_item, clear=False)

    def clear_list(self):
        if sp.is_maya():
            import maya.cmds as cmds
            if sys.solstice.dcc.shelf_exists(shelf_name=self.name):
                menu_items = cmds.shelfLayout(self.name, query=True, childArray=True)
                for item in menu_items:
                    try:
                        cmds.deleteUI(item)
                    except Exception:
                        pass
