#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya.py
# by Tomas Poveda
# Maya DCC implementation class
# ______________________________________________________________________
# ==================================================================="""

"""
Module that contains Maya definition
"""

from __future__ import print_function, division, absolute_import


from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import solstice_pipeline as sp
import maya.cmds as cmds
import maya.utils as utils
import maya.OpenMayaUI as OpenMayaUI
from solstice_pipeline.solstice_dcc import solstice_dcc
from solstice_pipeline.solstice_utils import solstice_maya_utils


class SolsticeMaya(solstice_dcc.SolsticeDCC, object):

    @staticmethod
    def get_name():
        """
        Returns the name of the DCC
        :return: str
        """

        return sp.SolsticeDCC.Maya

    @staticmethod
    def get_version():
        """
        Returns version of the DCC
        :return: int
        """

        return solstice_maya_utils.get_maya_version()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return solstice_maya_utils.get_maya_window()

    @staticmethod
    def execute_deferred(fn):
        """
        Executes given function in deferred mode
        """

        utils.executeDeferred(fn)

    @staticmethod
    def object_exists(node):
        """
        Returns whether given object exists or not
        :return: bool
        """

        return cmds.objExists(node)

    @staticmethod
    def object_type(node):
        """
        Returns type of given object
        :param node: str
        :return: str
        """

        return cmds.objectType(node)

    @staticmethod
    def check_object_type(node, node_type):
        """
        Returns whether give node is of the given type or not
        :param node: str
        :param node_type: str
        :return: bool
        """

        return cmds.objectType(node, isType=node_type)

    @staticmethod
    def node_type(node):
        """
        Returns node type of given object
        :param node: str
        :return: str
        """

        return cmds.nodeType(node)

    @staticmethod
    def all_scene_objects(full_path=True):
        """
        Returns a list with all scene nodes
        :param full_path: bool
        :return: list<str>
        """

        return cmds.ls(l=full_path)

    @staticmethod
    def select_object(node):
        """
        Selects given object in the current scene
        :param node: str
        """

        cmds.select(node)

    @staticmethod
    def clear_selection():
        """
        Clears current scene selection
        """

        cmds.select(clear=True)

    @staticmethod
    def delete_object(node):
        """
        Removes given node from current scene
        :param node: str
        """

        cmds.delete(node)

    @staticmethod
    def selected_nodes(full_path=True):
        """
        Returns a list of selected nodes
        :param full_path: bool
        :return: list<str>
        """

        return cmds.ls(sl=True, l=full_path)

    @staticmethod
    def node_short_name(node):
        """
        Returns short name of the given node
        :param node: str
        :return: str
        """

        return solstice_maya_utils.get_short_name(node)

    @staticmethod
    def node_namespace(node):
        """
        Returns namespace of the given node
        :param node: str
        :return: str
        """

        return cmds.referenceQuery(node, namespace=True)

    @staticmethod
    def node_parent_namespace(node):
        """
        Returns namespace of the given node parent
        :param node: str
        :return: str
        """

        return cmds.referenceQuery(node, parentNamespace=True)

    @staticmethod
    def node_is_referenced(node):
        """
        Returns whether given node is referenced or not
        :param node: str
        :return: bool
        """

        return cmds.referenceQuery(node, isNodeReferenced=True)

    @staticmethod
    def node_is_loaded(node):
        """
        Returns whether given node is loaded or not
        :param node: str
        :return: bool
        """

        return cmds.referenceQuery(node, isLoaded=True)

    @staticmethod
    def node_children(node, all_hierarchy=True, full_path=True):
        """
        Returns a list of children of the given node
        :param node: str
        :param all_hierarchy: bool
        :param full_path: bool
        :return: list<str>
        """

        return cmds.listRelatives(node, children=True, allDescendents=all_hierarchy, shapes=False, fullPath=full_path)

    @staticmethod
    def node_parent(node, full_path=True):
        """
        Returns parent node of the given node
        :param node: str
        :param full_path: bool
        :return: str
        """

        node_parent = cmds.listRelatives(node, parent=True, fullPath=full_path)
        if node_parent:
            node_parent = node_parent[0]

        return node_parent

    @staticmethod
    def node_root(node, full_path=True):
        """
        Returns hierarchy root node of the given node
        :param node: str
        :param full_path: bool
        :return: str
        """

        if not node:
            return None

        n = node
        while True:
            parent = cmds.listRelatives(n, parent=True, fullPath=full_path)
            if not parent:
                break
            n = parent[0]

        return n

    @staticmethod
    def set_parent(node, parent):
        """
        Sets the node parent to the given parent
        :param node: str
        :param parent: str
        """

        cmds.parent(node, parent)

    @staticmethod
    def node_nodes(node):
        """
        Returns referenced nodes of the given node
        :param node: str
        :return: list<str>
        """

        return cmds.referenceQuery(node, nodes=True)

    @staticmethod
    def node_filename(node, no_copy_number=True):
        """
        Returns file name of the given node
        :param node: str
        :param no_copy_number: bool
        :return: str
        """

        return cmds.referenceQuery(node, filename=True, withoutCopyNumber=no_copy_number)

    @staticmethod
    def list_node_types(type_string):
        """
        List all dependency node types satisfying given classification string
        :param type_string: str
        :return:
        """

        return cmds.listNodeTypes(type_string)

    @staticmethod
    def list_nodes(node_name=None, node_type=None):
        """
        Returns list of nodes with given types. If no type, all scene nodes will be listed
        :param node_name:
        :param node_type:
        :return:  list<str>
        """

        if not node_name and not node_type:
            return cmds.ls()

        if node_name and node_type:
            return cmds.ls(node_name, type=node_type)
        elif node_name and not node_type:
            return cmds.ls(node_name)
        elif not node_name and node_type:
            return cmds.ls(type=node_type)

    @staticmethod
    def list_children(node, all_hierarchy=True, full_path=True, children_type=None):
        """
        Returns a list of chlidren nodes of the given node
        :param node:
        :param all_hierarchy:
        :param full_path:
        :param children_type:
        :return:
        """

        if children_type:
            return cmds.listRelatives(node, children=True, allDescendents=all_hierarchy, fullPath=full_path, type=children_type)
        else:
            return cmds.listRelatives(node, children=True, allDescendents=all_hierarchy, fullPath=full_path)

    @staticmethod
    def list_relatives(node, all_hierarchy=True, full_path=True, relative_type=None, shapes=False, intermediate_shapes=False):
        """
        Returns a list of relative nodes of the given node
        :param node:
        :param all_hierarchy:
        :param full_path:
        :param relative_type:
        :param shapes:
        :param intermediate_shapes:
        :return:
        """

        if relative_type:

            return cmds.listRelatives(node, allDescendents=all_hierarchy, fullPath=full_path, type=relative_type, shapes=shapes, noIntermediate=not intermediate_shapes)
        else:
            return cmds.listRelatives(node, allDescendents=all_hierarchy, fullPath=full_path, shapes=shapes, noIntermediate=not intermediate_shapes)

    @staticmethod
    def list_shapes(node, full_path=True, intermediate_shapes=False):
        """
        Returns a list of shapes of the given node
        :param node: str
        :param full_path: bool
        :param intermediate_shapes: bool
        :return: list<str>
        """

        return cmds.listRelatives(node, shapes=True, fullPath=full_path, children=True, noIntermediate=not intermediate_shapes)

    @staticmethod
    def list_children_shapes(node, all_hierarchy=True, full_path=True, intermediate_shapes=False):
        """
        Returns a list of children shapes of the given node
        :param node:
        :param all_hierarchy:
        :param full_path:
        :param intermediate_shapes:
        :return:
        """

        return cmds.listRelatives(node, shapes=True, fullPath=full_path, children=True, allDescendents=all_hierarchy, noIntermediate=not intermediate_shapes)

    @staticmethod
    def list_materials():
        """
        Returns a list of materials in the current scene
        :return: list<str>
        """

        return cmds.ls(materials=True)

    @staticmethod
    def change_namespace(old_namespace, new_namespace):
        """
        Changes old namespace by a new one
        :param old_namespace: str
        :param new_namespace: str
        """

        return cmds.namespace(rename=[old_namespace, new_namespace])

    @staticmethod
    def change_filename(node, new_filename):
        """
        Changes filename of a given reference node
        :param node: str
        :param new_filename: str
        """

        return cmds.file(new_filename, loadReference=node)

    @staticmethod
    def import_reference(filename):
        """
        Imports object from reference node filename
        :param filename: str
        """

        return cmds.file(filename, importReference=True)

    @staticmethod
    def list_attributes(node):
        """
        Returns list of attributes of given node
        :param node: str
        :return: list<str>
        """

        return cmds.listAttr(node)

    @staticmethod
    def list_user_attributes(node):
        """
        Returns list of user defined attributes
        :param node: str
        :return: list<str>
        """

        return cmds.listAttr(node, userDefined=True)

    @staticmethod
    def add_string_attribute(node, attribute_name, keyable=False):
        """
        Adds a new string attribute into the given node
        :param node: str
        :param attribute_name: str
        :param keyable: bool
        """

        return cmds.addAttr(node, ln=attribute_name, dt='string', k=keyable)

    @staticmethod
    def attribute_exists(node, attribute_name):
        """
        Returns whether given attribute exists in given node
        :param node: str
        :param attribute_name: str
        :return: bool
        """

        return cmds.attributeQuery(attribute_name, node=node, exists=True)

    @staticmethod
    def lock_attribute(node, attribute_name):
        """
        Locks given attribute in given node
        :param node: str
        :param attribute_name: str
        """

        return cmds.setAttr('{}.{}'.format(node, attribute_name), lock=True)

    @staticmethod
    def unlock_attribute(node, attribute_name):
        """
        Locks given attribute in given node
        :param node: str
        :param attribute_name: str
        """

        return cmds.setAttr('{}.{}'.format(node, attribute_name), lock=False)

    @staticmethod
    def get_attribute_value(node, attribute_name):
        """
        Returns the value of the given attribute in the given node
        :param node: str
        :param attribute_name: str
        :return: variant
        """

        return cmds.getAttr('{}.{}'.format(node, attribute_name))

    @staticmethod
    def set_integer_attribute_value(node, attribute_name, attribute_value):
        """
        Sets the integer value of the given attribute in the given node
        :param node: str
        :param attribute_name: str
        :param attribute_value: int
        :return:
        """

        return cmds.setAttr('{}.{}'.format(node, attribute_name), int(attribute_value))

    @staticmethod
    def set_float_attribute_value(node, attribute_name, attribute_value):
        """
        Sets the integer value of the given attribute in the given node
        :param node: str
        :param attribute_name: str
        :param attribute_value: int
        :return:
        """

        return cmds.setAttr('{}.{}'.format(node, attribute_name), float(attribute_value))

    @staticmethod
    def set_string_attribute_value(node, attribute_name, attribute_value):
        """
        Sets the string value of the given attribute in the given node
        :param node: str
        :param attribute_name: str
        :param attribute_value: str
        """

        return cmds.setAttr('{}.{}'.format(node, attribute_name), str(attribute_value), type='string')

    @staticmethod
    def delete_attribute(node, attribute_name):
        """
        Deletes given attribute of given node
        :param node: str
        :param attribute_name: str
        """

        return cmds.deleteAttr(n=node, at=attribute_name)

    @staticmethod
    def list_connections(node, attribute_name):
        """
        List the connections of the given out attribute in given node
        :param node: str
        :param attribute_name: str
        :return: list<str>
        """

        return cmds.listConnections('{}.{}'.format(node, attribute_name))

    @staticmethod
    def list_connections_of_type(node, connection_type):
        """
        Returns a list of connections with the given type in the given node
        :param node: str
        :param connection_type: str
        :return: list<str>
        """

        return cmds.listConnections(node, type=connection_type)

    @staticmethod
    def list_source_destination_connections(node):
        """
        Returns source and destination connections of the given node
        :param node: str
        :return: list<str>
        """

        return cmds.listConnections(node, source=True, destination=True)

    @staticmethod
    def list_source_connections(node):
        """
        Returns source connections of the given node
        :param node: str
        :return: list<str>
        """

        return cmds.listConnections(node, source=True, destination=False)

    @staticmethod
    def list_destination_connections(node):
        """
        Returns source connections of the given node
        :param node: str
        :return: list<str>
        """

        return cmds.listConnections(node, source=False, destination=True)

    @staticmethod
    def new_file(force=True):
        """
        Creates a new file
        :param force: bool
        """

        cmds.file(new=True, f=force)

    @staticmethod
    def open_file(file_path, force=True):
        """
        Open file in given path
        :param file_path: str
        :param force: bool
        """

        return cmds.file(file_path, o=True, f=force)

    @staticmethod
    def is_plugin_loaded(plugin_name):
        """
        Return whether given plugin is loaded or not
        :param plugin_name: str
        :return: bool
        """

        return cmds.pluginInfo(plugin_name, query=True, loaded=True)

    @staticmethod
    def load_plugin(plugin_path, quiet=True):
        """
        Loads given plugin
        :param plugin_path: str
        :param quiet: bool
        """

        cmds.loadPlugin(plugin_path, quiet=True)

    @staticmethod
    def list_old_plugins():
        """
        Returns a list of old plugins in the current scene
        :return: list<str>
        """

        return cmds.unknownPlugin(query=True, list=True)

    @staticmethod
    def remove_old_plugin(plugin_name):
        """
        Removes given old plugin from current scene
        :param plugin_name: str
        """

        return cmds.unknownPlugin(plugin_name, remove=True)

    @staticmethod
    def scene_name():
        """
        Returns the name of the current scene
        :return: str
        """

        return cmds.file(query=True, sceneName=True)

    @staticmethod
    def scene_is_modified():
        """
        Returns whether current scene has been modified or not since last save
        :return: bool
        """

        return cmds.file(query=True, modified=True)

    @staticmethod
    def save_current_scene(force=True):
        """
        Saves current scene
        :param force: bool
        """

        return cmds.file(save=True, f=force)

    @staticmethod
    def confirm_dialog(title, message, button=None, cancel_button=None, default_button=None, dismiss_string=None):
        """
        Shows DCC confirm dialog
        :param title:
        :param message:
        :param button:
        :param cancel_button:
        :param default_button:
        :param dismiss_string:
        :return:
        """

        if button and cancel_button and dismiss_string and default_button:
            return cmds.confirmDialog(title=title, message=message, button=button, cancelButton=cancel_button, defaultButton=default_button, dismissString=dismiss_string)

        if button:
            return cmds.confirmDialog(title=title, message=message)
        else:
            return cmds.confirmDialog(title=title, message=message, button=button)

    @staticmethod
    def warning(message):
        """
        Prints a warning message
        :param message: str
        :return:
        """

        cmds.warning(message)

    @staticmethod
    def add_shelf_menu_item(parent, label, command='', icon=''):
        """
        Adds a new menu item
        :param parent:
        :param label:
        :param command:
        :param icon:
        :return:
        """

        return cmds.menuItem(parent=parent, label=label, command=command, image=icon or '')

    @staticmethod
    def add_shelf_sub_menu_item(parent, label, icon=''):
        """
        Adds a new sub menu item
        :param parent:
        :param label:
        :param icon:
        :return:
        """

        return cmds.menuItem(parent=parent, label=label, icon=icon or '', subMenu=True)

    @staticmethod
    def add_shelf_separator(shelf_name):
        """
        Adds a new separator to the given shelf
        :param shelf_name: str
        """

        return cmds.separator(parent=shelf_name, manage=True, visible=True, horizontal=False, style='shelf', enableBackground=False, preventOverride=False)


    @staticmethod
    def shelf_exists(shelf_name):
        """
        Returns whether given shelf already exists or not
        :param shelf_name: str
        :return: bool
        """

        return solstice_maya_utils.shelf_exists(shelf_name=shelf_name)

    @staticmethod
    def create_shelf(shelf_name, shelf_label=None):
        """
        Creates a new shelf with the given name
        :param shelf_name: str
        :param shelf_label: str
        """

        return solstice_maya_utils.create_shelf(name=shelf_name)

    @staticmethod
    def delete_shelf(shelf_name):
        """
        Deletes shelf with given name
        :param shelf_name: str
        """

        return solstice_maya_utils.delete_shelf(shelf_name=shelf_name)

    @staticmethod
    def select_file_dialog(title, start_directory=None, pattern=None):
        """
        Shows select file dialog
        :param title: str
        :param start_directory: str
        :param pattern: str
        :return: str
        """

        res = cmds.fileDialog2(fm=1, dir=start_directory, cap=title, ff=pattern)
        if res:
            res = res[0]

        return res

    @staticmethod
    def select_folder_dialog(title, start_directory=None):
        """
        Shows select folder dialog
        :param title: str
        :param start_directory: str
        :return: str
        """

        res = cmds.fileDialog2(fm=3, dir=start_directory, cap=title)
        if res:
            res = res[0]

        return res

    @staticmethod
    def get_current_frame():
        """
        Returns current frame set in time slider
        :return: int
        """

        return solstice_maya_utils.get_current_frame()

    @staticmethod
    def get_time_slider_range():
        """
        Return the time range from Maya time slider
        :return: list<int, int>
        """

        return solstice_maya_utils.get_time_slider_range(highlighted=False)

    @staticmethod
    def refresh_viewport():
        """
        Refresh current DCC viewport
        """

        cmds.refresh()
