#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya.py
# by Tomas Poveda
# Maya DCC implementation class
# ______________________________________________________________________
# ==================================================================="""

"""
Module that contains Maya definition
"""

from __future__ import print_function, division, absolute_import


import solstice_pipeline as sp
import maya.cmds as cmds
from solstice_pipeline.solstice_utils import solstice_maya_utils


class SolsticeMaya(object):

    @staticmethod
    def get_name():
        """
        Returns the name of the DCC
        :return: str
        """

        return sp.SolsticeDCC.Maya

    @staticmethod
    def get_version():
        """
        Returns version of the DCC
        :return: int
        """

        return solstice_maya_utils.get_maya_version()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return solstice_maya_utils.get_main_window()

    @staticmethod
    def object_exists(node):
        """
        Returns whether given object exists or not
        :return: bool
        """

        return cmds.objExists(node)
