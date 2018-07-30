#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_studentcheck.py
# by Tomas Poveda
# Checks for student license and fix the problem if necessary
# ______________________________________________________________________
# ==================================================================="""

import os

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_checks import solstice_check
from solstice_pipeline.solstice_utils import solstice_maya_utils

