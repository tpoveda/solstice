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

# TODO: Take in account namespaces

def selectGlobalControl():
    cmds.select('main_set', replace=True)

def selectMainControl():
    cmds.select('main_ctrl', replace=True)

def selectDynamicControl():
    cmds.select('dynamicParent_ctrl', replace=True)

def selectAllControls():
    cmds.select('CTRLs_set', replace=True)

def selectBodyControls():
    cmds.select('fingerSystem1_set', replace=True)
    cmds.select('head1_set', add=True)
    cmds.select('L_arm1_set', add=True)
    cmds.select('L_leg1_set', add=True)
    cmds.select('R_arm1_set', add=True)
    cmds.select('R_leg1_set', add=True)
    cmds.select('spine1_set', add=True)

def selectFaceControls():
    cmds.select('face1_set', replace=True)

def setKeyframe():
    mel.eval('setKeyframe;')


def clearSelection():
    cmds.select(clear=True)

def resetAttributes(ctrl):
    mel.eval('vl_resetAttributes("{}")'.format(ctrl))