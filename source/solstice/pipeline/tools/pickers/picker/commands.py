#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Module that contains different commands used by pickers
# ==================================================================="""

import maya.cmds as cmds
import maya.mel as mel


def select_control(ctrl_name, replace=True):

    from pipeline.pickers.picker import pickerwindow

    window_picker = pickerwindow.window_picker
    if window_picker and window_picker.namespace and window_picker.namespace.count() > 0:
        ctrl = '{0}:{1}'.format(window_picker.namespace.currentText(), ctrl_name)
    else:
        ctrl = ctrl_name

    if cmds.objExists(ctrl):
        cmds.select(ctrl, replace=replace, add=not replace)


def select_global_control():
    select_control('global_ctrl')


def select_main_control():
    select_control('main_ctrl')


def select_dynamic_control():
    select_control('dynamicParent_ctrl')


def select_all_controls():
    select_control('CTRLs_set')


def select_body_controls():
    select_control('fingerSystem1_set')
    select_control('head1_set', replace=False)
    select_control('L_arm1_set', replace=False)
    select_control('L_leg1_set', replace=False)
    select_control('R_arm1_set', replace=False)
    select_control('R_leg1_set', replace=False)
    select_control('spine1_set', replace=False)


def select_face_controls():
    select_control('face1_set')


def set_keyframe():
    mel.eval('setKeyframe;')


def clear_selection():
    cmds.select(clear=True)


def reset_attributes(ctrl):
    mel.eval('vl_resetAttributes("{}")'.format(ctrl))
