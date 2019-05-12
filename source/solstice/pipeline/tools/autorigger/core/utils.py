#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions for rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import maya.cmds as cmds


def lock_all_transforms(name, lock_visibility=False):
    """
    Util function to lock rig controls transforms easily
    :param name: str, name of the control we want to lock transform channels of
    :param lock_visibility: bool, Whether visibility needs to be also locked or not
    """

    for axis in ['x', 'y', 'z']:
        for xform in ['t', 'r', 's']:
            cmds.setAttr('{}.{}{}'.format(name, xform, axis), lock=True, keyable=False, channelBox=False)
    if lock_visibility:
        cmds.setAttr('{}.visibility'.format(name), False)
        cmds.setAttr('{}.visibility'.format(name), lock=True, keyable=False, channelBox=False)


def snap(node, target):
    """
    Snaps node to given target
    :param node: str
    :param target: str
    """

    cmds.delete(cmds.pointConstraint(target, node, mo=False))


def match(node, target):
    """
    Matches node transform to given target transform
    :param node: str
    :param target: str
    """

    cmds.delete(cmds.parentConstraint(target, node, mo=False))
