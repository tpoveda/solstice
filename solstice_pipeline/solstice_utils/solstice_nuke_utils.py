#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities functions for Houdini
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import nuke


def get_nuke_version(as_string=True):
    """
    Returns version of the executed Nuke
    @returns: str, version of Houdini
    """

    if as_string:
        return nuke.NUKE_VERSION_STRING
    else:
        return [nuke.NUKE_VERSION_MAJOR, nuke.NUKE_VERSION_MINOR]


def get_nuke_window():
    """
    Return the Nuke Qt main window widget
    """

    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
            return widget

    return None