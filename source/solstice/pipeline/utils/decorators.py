#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful decorators
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp

if sp.is_maya():
    import maya.cmds as cmds


def solstice_undo(fn):

    """
    Simple undo wrapper. Use @solstice_undo above the function to wrap it.
    @param fn: function to wrap
    @return wrapped function
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper