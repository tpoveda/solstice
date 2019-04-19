#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nuke DCC implementation class
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.dcc.core import dcc
from solstice.pipeline.utils import nukeutils


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
