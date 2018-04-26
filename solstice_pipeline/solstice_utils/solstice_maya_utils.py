#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Maya
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *
try:
    from shiboken2 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
import maya.OpenMayaUI as OpenMayaUI


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