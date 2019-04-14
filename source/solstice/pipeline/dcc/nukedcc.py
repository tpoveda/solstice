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


import pipeline as sp
from pipeline.dcc import dcc
from pipeline.utils import nukeutils


class SolsticeNuke(dcc.SolsticeDCC, object):

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

        return nukeutils.get_nuke_window()

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        return nukeutils.get_nuke_window()
