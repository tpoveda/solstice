#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerDataGenerator.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Tool that automatically generates a picker data from a current character rig file
______________________________________________________________________
==================================================================="""

import maya.cmds as cmds
import re

def getData(parts):

    # Init data
    data = { 'fileType':'pickerData', 'offset':'15', 'pickerButtons':
        {

        }
    }

    # Add parts to data
    for part in parts:
        data['pickerButtons'][part] = {}

    # sceneObjects = cmds.ls('*_ctrl', type='transform')
    # validCtrls = []
    # invalidCtrls = []
    #
    # for ctrl in sceneObjects:
    #     if re.match('.*_.*_.*_.*', ctrl):
    #         print ctrl

    return data