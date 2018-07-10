#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Maya
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtWidgets import *
try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya

import solstice_pipeline as sp

_DPI_SCALE = 1.0 if not hasattr(cmds, "mayaDpiSetting") else cmds.mayaDpiSetting(query=True, realScaleValue=True)


class MCallbackIdWrapper(object):
    """
    Wrapper class to handle cleaning up of MCallbackIds from registered MMessages
    """

    def __init__(self, callback_id):
        super(MCallbackIdWrapper, self).__init__()
        self.callback_id = callback_id
        sp.logger.debug('Adding Callback: %s' % self.callback_id)

    def __del__(self):
        try:
            OpenMaya.MDGMessage.removeCallback(self.callback_id)
        except Exception:
            pass
        try:
            OpenMaya.MMessage.removeCallback(self.callback_id)
        except Exception:
            pass
        sp.logger.debug('Removing Callback: %s' % self.callback_id)

    def __repr__(self):
        return 'MCallbackIdWrapper(%r)' % self.callback_id


def get_maya_api_version():
    """
    Returns Maya API version
    :return: int
    """

    return int(cmds.about(api=True))


def get_maya_window():
    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(long(ptr), QMainWindow)

    return None


def get_main_shelf():
    """
    Returns the Maya main shelf
    """

    return mel.eval('$tempVar = $gShelfTopLevel')


def get_main_window():
    """
    Returns Maya main window through MEL
    """

    return mel.eval("$tempVar = $gMainWindow")


def viewport_message(text):
    """
    Shows a message in the Maya viewport
    :param text: str, text to show in Maya viewport
    """

    cmds.inViewMessage(amg='<hl>{}</hl>'.format(text), pos='midCenter', fade=True)


def force_stack_trace_on():
    """
    Forces enabling Maya Stack Trace
    """

    try:
        mel.eval('stackTrace -state on')
        cmds.optionVar(intValue=('stackTraceIsOn', True))
        what_is = mel.eval('whatIs "$gLastFocusedCommandReporter"')
        if what_is != 'Unknown':
            last_focused_command_reporter = mel.eval('$tmp = $gLastFocusedCommandReporter')
            if last_focused_command_reporter and last_focused_command_reporter != '':
                mel.eval('synchronizeScriptEditorOption 1 $stackTraceMenuItemSuffix')
    except RuntimeError:
        pass


def pass_message_to_main_thread(message_handler, *args):
    """
    Executes teh message_handler with the given list of arguments in Maya's main thread
    during the next idle event
    :param message_handler: variant, str || function, string containing Python code or callable function
    """

    utils.executeInMainThreadWithResult(message_handler, *args)


def get_upstream_nodes(node):
    """
    Return a list with all upstream nodes of the given Maya node
    :param node: str, name of the node
    :return: lsitzstr>
    """

    upstream_nodes = list()
    upstream_nodes.append(node)
    incoming_nodes = cmds.listConnections(node, source=True, destination=False)
    if incoming_nodes:
        for n in incoming_nodes:
            upstream_nodes.extend(get_upstream_nodes(n))
        return upstream_nodes
    else:
        return upstream_nodes


def delete_all_incoming_nodes(node):
    """
    Delete all incoming nodes from the given Maya node
    :param node: str
    :param attrs: list<str>
    """

    upstream_nodes = list()
    upstream_nodes_clean = list()
    connections = cmds.listConnections(node, source=True, destination=False)
    if connections:
        for node in connections:
            upstream_nodes.extend(get_upstream_nodes(node))

        for node in upstream_nodes:
            if node not in upstream_nodes_clean:
                upstream_nodes_clean.append(node)

        for node in upstream_nodes_clean:
            cmds.delete(node)


def remove_callback(callback_id):
    try:
        OpenMaya.MEventMessage.removeCallback(callback_id)
        return
    except Exception:
        pass
    try:
        OpenMaya.MDGMessage.removeCallback(callback_id)
        return
    except Exception:
        pass


def dpi_scale(value):
    return _DPI_SCALE * value


def shelf_exists(shelf_name):
    """
    Returns True if the given shelf name already exists or False otherwise
    :param shelf_name: str, shelf name
    :return: bool
    """

    return cmds.shelfLayout(shelf_name, exists=True)


def delete_shelf(shelf_name):
    """
    Deletes given shelf by name, if exists
    :param shelf_name: str, shelf name
    """

    if shelf_exists(shelf_name=shelf_name):
        cmds.deleteUI(shelf_name)


def create_shelf(name, parent_layout='ShelfLayout'):
    """
    Creates a new shelf parented on the given layout
    :param name: str, name of the shelf to create
    :param parent_layout: name of the parent shelf layout
    :return: str
    """

    return cmds.shelfLayout(name, parent=parent_layout)


def get_top_maya_shelf():
    return mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")


def get_all_shelves():
    return cmds.tabLayout(get_top_maya_shelf(), query=True, ca=True)


def get_current_shelf():
    return cmds.tabLayout(get_top_maya_shelf(), query=True, st=True)


def main_menu():
    """
    Returns Maya main menu
    """

    return mel.eval('$tmp=$gMainWindow')


def get_menus():
    """
    Return a list with all Maya menus
    :return: list<str>
    """

    return cmds.lsUI(menus=True)


def remove_menu(menu_name):
    """
    Removes, if exists, a menu of Max
    :param menu_name: str, menu name
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            cmds.deleteUI(m, menu=True)


def check_menu_exists(menu_name):
    """
    Returns True if a menu with the given name already exists
    :param menu_name: str, menu name
    :return: bol
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            return True

    return False


def find_menu(menu_name):
    """
    Returns Menu instance by the given name
    :param menu_name: str, menu of the name to search for
    :return: nativeMenu
    """

    for m in get_menus():
        lbl = cmds.menu(m, query=True, label=True)
        if lbl == menu_name:
            return m

    return None
