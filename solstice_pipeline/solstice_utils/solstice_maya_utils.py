#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Maya
# ______________________________________________________________________
# ==================================================================="""

import os
import contextlib
from collections import OrderedDict

from solstice_qt.QtWidgets import *
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


def maya_undo(fn):
    """
    Undo function decorator for Maya function calls
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret

    return wrapper


@contextlib.contextmanager
def maya_no_undo():
    """
    Disable undo functionality during the context
    """

    try:
        cmds.undoInfo(stateWithoutFlush=False)
        yield
    finally:
        cmds.undoInfo(stateWithoutFlush=True)


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
        return wrapInstance(long(ptr), QWidget)

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


def get_plugin_shapes():
    """
    Return all available plugin shapes
    :return: dict, plugin shapes by their menu label and script name
    """

    filters = cmds.pluginDisplayFilter(query=True, listFilters=True)
    labels = [cmds.pluginDisplayFilter(f, query=True, label=True) for f in filters]
    return OrderedDict(zip(labels, filters))


def get_current_scene_name():
    """
    Returns the name of the current scene opened in Maya
    :return: str
    """

    scene_path = cmds.file(query=True, sceneName=True)
    if scene_path:
        return os.path.splitext(os.path.basename(scene_path))[0]

    return None


def get_current_camera():
    """
    Returns the currently active camera
    :return: str, name of the active camera transform
    """

    panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=panel) == 'modelPanel':
        cam = cmds.modelEditor(panel, query=True, camera=True)
        if cam:
            if cmds.nodeType(cam) == 'transform':
                return cam
            elif cmds.objectType(cam, isAType='shape'):
                parent = cmds.listRelatives(cam, parent=True, fullPath=True)
                if parent:
                    return parent[0]

    cam_shapes = cmds.ls(sl=True, type='camera')
    if cam_shapes:
        return cmds.listRelatives(cam_shapes, parent=True, fullPath=True)[0]

    transforms = cmds.ls(sl=True, type='transform')
    if transforms:
        cam_shapes = cmds.listRelatives(transforms, shapes=True, type='camera')
        if cam_shapes:
            return cmds.listRelatives(cam_shapes, parent=True, fullPath=True)[0]


def get_active_editor():
    """
    Returns the active editor panel of Maya
    """

    cmds.currentTime(cmds.currentTime(query=True))
    panel = cmds.playblast(activeEditor=True)
    return panel.split('|')[-1]


def get_current_frame():
    """
    Return current Maya frame set in time slier
    :return: int
    """

    return cmds.currentTime(query=True)


def get_time_slider_range(highlighted=True, within_highlighted=True, highlighted_only=False):
    """
    Return the time range from Maya time slider
    :param highlighted: bool, If True it will return a selected frame range (if there is any selection of more than one frame) else
    it will return min and max playblack time
    :param within_highlighted: bool, Maya returns the highlighted range end as a plus one value by default. If True, this is fixed by
    removing one from the last frame number
    :param highlighted_only: bool, If True, it wil return only highlighted frame range
    :return: list<float, float>, [start_frame, end_frame]
    """

    if highlighted is True:
        playback_slider = mel.eval("global string $gPlayBackSlider; " "$gPlayBackSlider = $gPlayBackSlider;")
        if cmds.timeControl(playback_slider, query=True, rangeVisible=True):
            highlighted_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            if within_highlighted:
                highlighted_range[-1] -= 1
            return highlighted_range

    if not highlighted_only:
        return [cmds.playbackOptions(query=True, minTime=True), cmds.playbackOptions(query=True, maxTime=True)]


def get_current_render_layer():
    """
    Returns the current Maya render layer
    :return: str
    """

    return cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)


def get_playblast_formats():
    """
    Returns all formats available for Maya playblast
    :return: list<str>
    """

    cmds.currentTime(cmds.currentTime(query=True))
    return cmds.playblast(query=True, format=True)


def get_playblast_compressions(format='avi'):
    """
    Returns playblast compression for the given format
    :param format: str, format to check compressions for
    :return: list<str>
    """

    cmds.currentTime(cmds.currentTime(query=True))
    return mel.eval('playblast -format "{0}" -query -compression'.format(format))
