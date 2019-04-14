#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Utility functions for Solstice Pickers
# ==================================================================="""

import os

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *
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

import pipeline as sp

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
        sp.logger.error('ERROR: Impossible to load {} script'.format(name))
        return
    try:
        sp.logger.debug('Loading MEL script: {}'.format(name))
        mel.eval('source "{}"'.format(script_to_load).replace('\\', '/'))
        sp.logger.debug('MEL script {} loaded successfully!'.format(name))
    except Exception as e:
        cmds.error('ERROR: Impossible to evaluation {} script'.format(name))
        print '-' * 100
        print str(e)


def load_vl_scripts():
    """
    Loads all vl picker scripts
    """

    if not os.path.exists(scripts_path):
        cmds.error('Solstice Picker Scripts not found!')

    sp.logger.debug('Loading pickers MEL scripts ...')

    load_script('vlRigIt_getModuleFromControl.mel')
    load_script('vlRigIt_getControlsFromModuleList.mel')
    load_script('vlRigIt_selectModuleControls.mel')
    load_script('vlRigIt_snap_ikFk.mel')
    load_script('vl_resetTransformations.mel')
    load_script('vl_resetAttributes.mel')
    load_script('vl_contextualMenuBuilder.mel')


def get_mirror_control(ctrl_name):
    """
    Mirror control
    :param ctrl_name: str
    """

    old_side = None
    new_side = None
    sides_list = ['l', 'r', 'L', 'R']
    side_formats = []
    for side in sides_list:
        side_formats.append('{0}_'.format(side))
        side_formats.append('_{0}_'.format(side))
        side_formats.append('_{0}'.format(side))

    # If the control name, we do not take in accout namespace
    name_parts = ctrl_name.rpartition(':')
    namespace = None
    if len(name_parts) > 1:
        namespace = name_parts[0]
    ctrl_name = name_parts[2]

    for format in side_formats:
        if format in ctrl_name:
            for side in sides_list:
                if side in format:
                    old_side = side
                    break

    if old_side is None:
        return

    if old_side == 'l' or old_side == 'L':
        new_side = 'R'
    elif new_side == 'r' or old_side == 'R':
        new_side = 'L'

    if new_side is None:
        return

    if namespace:
        return namespace + ':' + ctrl_name.replace(old_side, new_side)
    else:
        return ctrl_name.replace(old_side, new_side)
