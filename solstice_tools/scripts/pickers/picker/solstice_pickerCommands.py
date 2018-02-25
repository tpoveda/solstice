#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerCommands.py
by Tomás Poveda
Custom commands used by the picker of Solstice Short Film
______________________________________________________________________
Module that contains differents commands used by pickers
______________________________________________________________________
==================================================================="""

import maya.cmds as cmds
import maya.mel as mel

from pickers.picker import solstice_pickerWindow

# TODO: Take in account namespaces

def selectGlobalControl():
    _select_control('global_ctrl')


def selectMainControl():
    _select_control('main_ctrl')


def selectDynamicControl():
    _select_control('dynamicParent_ctrl')


def selectAllControls():
    _select_control('CTRLs_set')


def selectBodyControls():
    _select_control('fingerSystem1_set')
    _select_control('head1_set', replace=False)
    _select_control('L_arm1_set', replace=False)
    _select_control('L_leg1_set', replace=False)
    _select_control('R_arm1_set', replace=False)
    _select_control('R_leg1_set', replace=False)
    _select_control('spine1_set', replace=False)


def selectFaceControls():
    _select_control('face1_set')


def setKeyframe():
    mel.eval('setKeyframe;')


def clearSelection():
    cmds.select(clear=True)


def resetAttributes(ctrl):
    mel.eval('vl_resetAttributes("{}")'.format(ctrl))


def _select_control(ctrl_name, replace=True):
    window_picker = solstice_pickerWindow.window_picker
    if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
        ctrl = '{0}:{1}'.format(window_picker.namespace.currentText(), ctrl_name)
    else:
        ctrl = ctrl_name

    if cmds.objExists(ctrl):
        cmds.select(ctrl, replace=replace, add=not replace)