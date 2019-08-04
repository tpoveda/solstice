#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful utilities functions for Nuke
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtWidgets import *

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
