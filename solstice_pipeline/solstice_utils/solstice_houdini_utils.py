#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Houdini
# ______________________________________________________________________
# ==================================================================="""

import solstice_pipeline as sp

if sp.is_houdini():
    import hou
    import hdefereval


def get_houdini_version(as_string=True):
    """
    Returns version of the executed Houdini
    @returns: str, version of Houdini
    """

    if as_string:
        return hou.applicationVersionString()
    else:
        return hou.applicationVersion()


def get_houdini_window():
    """
    Return the Houdini main window widget as a Python object
    """

    return hou.ui.mainQtWindow()


def get_houdini_pass_main_thread_function():
    """
    Return Houdini function to execute function in Houdini main thread
    :return: fn
    """

    return hdefereval.executeInMainThreadWithResult
