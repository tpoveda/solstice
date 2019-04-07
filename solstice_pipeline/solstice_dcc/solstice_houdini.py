#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya.py
# by Tomas Poveda
# Houdini DCC implementation class
# ______________________________________________________________________
# ==================================================================="""

"""
Module that contains Houdini definition
"""
from __future__ import print_function, division, absolute_import


import solstice_pipeline as sp
import hou
from solstice_pipeline.solstice_utils import solstice_houdini_utils


class SolsticeHoudini(object):

    @staticmethod
    def get_name():
        """
        Returns the name of the DCC
        :return: str
        """

        return sp.SolsticeDCC.Houdini

    @staticmethod
    def get_version():
        """
        Returns version of the DCC
        :return: int
        """

        return solstice_houdini_utils.get_houdini_version()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return solstice_houdini_utils.get_houdini_window()

    @staticmethod
    def object_exists(node):
        """
        Returns whether given object exists or not
        :return: bool
        """

        hou_node = hou.node(node)
        if hou_node:
            return True

        return False
