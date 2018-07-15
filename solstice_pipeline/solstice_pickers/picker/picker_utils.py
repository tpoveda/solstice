#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Utility functions for Solstice Pickers
# ==================================================================="""

import os

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
try:
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from shiboken import wrapInstance
    except ImportError, e:
        print e

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as OpenMayaUI


# --------------------------------------------------------------------------------------------
scripts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'scripts')
# --------------------------------------------------------------------------------------------


def dock_window(picker_name, picker_title, character_name, dialog_class):
    try:
        cmds.deleteUI(picker_name)
    except Exception:
        pass

    main_control = cmds.workspaceControl(picker_name, ttc=["AttributeEditor", -1], iw=300, mw=True, wp='preferred', label=picker_title)

    control_widget = OpenMayaUI.MQtUtil.findControl(picker_name)
    control_wrap = wrapInstance(long(control_widget), QWidget)
    control_wrap.setAttribute(Qt.WA_DeleteOnClose)
    win = dialog_class(picker_name, picker_title, character_name, control_wrap)

    cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

    return win.run()


def get_global_variable(var_name):
    """
    Returns the value of a MEL global variable
    :param var_name: sr, name of MEL global variable
    :return: str
    """

    return mel.eval("$tempVar = {0}".format(var_name))


def set_tool(name):
    """
    Sets the current tol (translate, rotate, scale) that is being used inside Maya viewport
    :param name: str, name of the tool to use ('translate', 'rotate', 'scale')
    """

    context_lookup = {
        'move': "$gMove",
        'rotate': "$gRotate",
        'scale': "$gSacle"
    }
    tool_context = get_global_variable(context_lookup[name])
    cmds.setToolTo(tool_context)


def get_maya_window():
    """
    Returns an instance of the Maya main window
    """

    maya_main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(maya_main_window_ptr), QWidget)


def get_maya_api_version():
    """
    Returns Maya API version
    :return: int
    """

    return int(cmds.about(api=True))


def picker_undo(fn):
    """
    Undo function decorator for picker actions
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret

    return wrapper


def load_script(name):
    """
    Function that loads a given MEL script by its name
    :param name: str, name of the script to load
    """

    script_to_load = os.path.join(scripts_path, name)
    if not os.path.isfile(script_to_load):
        cmds.error('ERROR: Impossible to load {} script'.format(name))
        return
    try:
        mel.eval('source "{}"'.format(script_to_load).replace('\\', '/'))
    except Exception as e:
        cmds.error('ERROR: Impossible to evaluation {} script'.format(name))
        print '-' * 100
        print str(e)
