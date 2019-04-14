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


import solstice_pipeline as sp
from solstice_pipeline.solstice_dcc import solstice_dcc
from solstice_pipeline.solstice_utils import solstice_nuke_utils


class SolsticeNuke(solstice_dcc.SolsticeDCC, object):

    @staticmethod
    def get_name():
        """
        Returns the name of the DCC
        :return: str
        """

        return sp.SolsticeDCC.Nuke

    @staticmethod
    def get_version():
        """
        Returns version of the DCC
        :return: int
        """

        return solstice_nuke_utils.get_nuke_window()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return solstice_nuke_utils.get_nuke_window()
