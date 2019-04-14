#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya.py
# by Tomas Poveda
# Houdini DCC implementation class
# ______________________________________________________________________
# ==================================================================="""


from __future__ import print_function, division, absolute_import


import hou
import hdefereval

import pipeline as sp
from pipeline.dcc import dcc
from pipeline.utils import houdiniutils


class SolsticeHoudini(dcc.SolsticeDCC, object):

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

        return houdiniutils.get_houdini_version()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return houdiniutils.get_houdini_window()

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

        return houdiniutils.shelf_exists(shelf_name=shelf_name)

    @staticmethod
    def create_shelf(shelf_name, shelf_label=None):
        """
        Creates a new shelf with the given name
        :param shelf_name: str
        :param shelf_label: str
        """

        return houdiniutils.create_shelf(shelf_name=shelf_name, shelf_label=shelf_label)

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

    @staticmethod
    def get_current_frame():
        """
        Returns current frame set in time slider
        :return: int
        """

        return houdiniutils.get_current_frame()

    @staticmethod
    def get_time_slider_range():
        """
        Return the time range from Maya time slider
        :return: list<int, int>
        """

        return houdiniutils.get_time_slider_range()
