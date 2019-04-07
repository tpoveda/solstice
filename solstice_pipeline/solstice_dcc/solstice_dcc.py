#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_dcc.py
# by Tomas Poveda
# Base DCC abstract definition class
# ______________________________________________________________________
# ==================================================================="""

"""
Module that contains abstract definition of basic DCC functions
"""

from __future__ import print_function, division, absolute_import


class SolsticeDCC(object):

    @staticmethod
    def get_name():
        """
        Returns the name of the DCC
        :return: str
        """

        raise NotImplementedError('abstract DCC function get_name() not implemented!')

    @staticmethod
    def get_version():
        """
        Returns version of the DCC
        :return: int
        """

        raise NotImplementedError('abstract DCC function get_version() not implemented!')

    @staticmethod
    def get_main_window():
        """
        Returns Qt object that references to the main DCC window
        :return:
        """

        raise NotImplementedError('abstract DCC function get_main_window() not implemented!')


    @staticmethod
    def object_exists(node):
        """
        Returns whether given object exists or not
        :return: bool
        """

        raise NotImplementedError('abstract DCC function object_exists() not implemented!')

