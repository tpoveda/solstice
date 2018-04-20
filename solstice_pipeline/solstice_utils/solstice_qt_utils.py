#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_qt_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for PySide
# ______________________________________________________________________
# ==================================================================="""

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

from Qt.QtCore import *
from Qt.QtWidgets import *
try:
    from shiboken import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

import solstice_pipeline as sp
from solstice_utils import solstice_maya_utils


def dock_solstice_widget(widget_class):

    workspace_control = widget_class.__name__ + '_workspace_control'

    try:
        cmds.deleteUI(workspace_control)
        sp.logger.debug('Removing workspace {0}'.format(workspace_control))
    except:
        pass

    if solstice_maya_utils.get_maya_api_version() >= 201700:

        main_control = cmds.workspaceControl(workspace_control, ttc=["AttributeEditor", -1], iw=425, mw=True, wp='preferred', label='{0} - {1}'.format(widget_class.title, widget_class.version))
        control_widget = OpenMayaUI.MQtUtil.findControl(workspace_control)
        control_wrap = wrapInstance(long(control_widget), QWidget)
        control_wrap.setAttribute(Qt.WA_DeleteOnClose)
        win = widget_class(name=workspace_control, parent=control_wrap, layout=control_wrap.layout())
        cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))
    else:
        pass

    return win

