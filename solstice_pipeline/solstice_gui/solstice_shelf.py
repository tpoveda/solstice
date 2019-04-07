#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shelf.py
# by Tomas Poveda
# Module that contains base class to create Solstice Shelf
# ______________________________________________________________________
# ==================================================================="""

import json
from collections import OrderedDict
from functools import partial

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_qt_utils as qt
from solstice_pipeline.resources import solstice_resource

if sp.is_maya():
    import maya.cmds as cmds
    import maya.mel as mel
    import maya.OpenMayaUI as OpenMayaUI
    from solstice_utils import solstice_maya_utils as utils


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

        return cmds.menuItem(parent=parent, label=label, command=command, image=icon or '')

    @staticmethod
    def add_sub_menu(parent, label, icon=None):
        """
        Adds a sub menu item with the given label and icon to the given parent popup menu
        :param parent:
        :param label:
        :param icon:
        :return:
        """

        return cmds.menuItem(parent=parent, label=label, icon=icon or '', subMenu=True)

    def create(self, delete_if_exists=True):
        """
        Creates a new shelf
        """

        if delete_if_exists:
            if utils.shelf_exists(shelf_name=self.name):
                utils.delete_shelf(shelf_name=self.name)
        else:
            assert not utils.shelf_exists(self.name), 'Shelf with name {} already exists!'.format(self.name)

        self.name = utils.create_shelf(name=self.name)

        # ========================================================================================================

        self.category_btn = QPushButton('')
        self.category_btn.setIcon(solstice_resource.icon('solstice_s'))
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

        cmds.separator(parent=self.name, manage=True, visible=True, horizontal=False, style='shelf', enableBackground=False, preventOverride=False)

    def build_category(self, shelf_file, category_name):

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
            # self.add_separator()

        with open(shelf_file) as f:
            shelf_data = json.load(f, object_pairs_hook=OrderedDict)
            if not 'solstice_shelf' in shelf_data:
                sp.logger.warning('Impossible to create Solstice Shelf! Please contact TD!')
                return

            for item, item_data in shelf_data['solstice_shelf'].items():
                if item != category_name:
                    continue

                for i in item_data:
                    icon = i.get('icon')
                    command = i.get('command')
                    annotation = i.get('annotation')
                    label = i.get('label')

                    if annotation == 'separator':
                        self.add_separator()
                    else:
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
                sp.logger.warning('Impossible to create Solstice Shelf! Please contact TD!')
                return

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
        if utils.shelf_exists(shelf_name=self.name):
            menu_items = cmds.shelfLayout(self.name, query=True, childArray=True)
            for item in menu_items:
                try:
                    cmds.deleteUI(item)
                except Exception:
                    pass