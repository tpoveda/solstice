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
import hdefereval

from solstice_pipeline.solstice_dcc import solstice_dcc
from solstice_pipeline.solstice_utils import solstice_houdini_utils


class SolsticeHoudini(solstice_dcc.SolsticeDCC, object):

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
    def execute_deferred(fn):
        """
        Executes given function in deferred mode
        """

        hdefereval.executeDeferred(fn)

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

    @staticmethod
    def shelf_exists(shelf_name):
        """
        Returns whether given shelf already exists or not
        :param shelf_name: str
        :return: bool
        """

        return solstice_houdini_utils.shelf_exists(shelf_name=shelf_name)

    @staticmethod
    def create_shelf(shelf_name, shelf_label=None):
        """
        Creates a new shelf with the given name
        :param shelf_name: str
        :param shelf_label: str
        """

        return solstice_houdini_utils.create_shelf(shelf_name=shelf_name, shelf_label=shelf_label)

    @staticmethod
    def select_file_dialog(title, start_directory=None, pattern=None):
        """
        Shows select file dialog
        :param title: str
        :param start_directory: str
        :param pattern: str
        :return: str
        """

        return hou.ui.selectFile(start_directory=start_directory, title=title, pattern=pattern)
