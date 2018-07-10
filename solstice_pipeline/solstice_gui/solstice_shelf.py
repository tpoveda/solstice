#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shelf.py
# by Tomas Poveda
# Module that contains base class to create Solstice Shelf
# ______________________________________________________________________
# ==================================================================="""

import xml.dom.minidom as minidom

import maya.cmds as cmds
import maya.mel as mel

from solstice_utils import solstice_maya_utils as utils


class SolsticeShelf(object):
    def __init__(self, name='Solstice', label_background=(0, 0, 0, 0), label_color=(0.9, 0.9, 0.9)):
        super(SolsticeShelf, self).__init__()

        self.name = name
        self.label_background = label_background
        self.label_color = label_color

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

    # endregion

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

    def build(self, shelf_file):
        """
        Builds shelf
        :param shelf_file: str
        """
        xml_menu_doc = minidom.parse(shelf_file)
        for shelf_item in xml_menu_doc.getElementsByTagName('shelfItem'):
            btn_icon = shelf_item.attributes['icon'].value
            btn_annotation = shelf_item.attributes['ann'].value
            btn_command = shelf_item.attributes['cmds'].value
            btn_lbl = shelf_item.attributes['label'].value or ''
            if btn_annotation == 'Separator':
                self.add_separator()
            else:
                self.add_button(label=btn_lbl, command=btn_command, icon=btn_icon, tooltip=btn_annotation)
