#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains generic checks
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys

import solstice.pipeline as sp
from solstice.pipeline.tools.sanitycheck.checks import check

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.utils import mayautils


class StudentLicenseCheck(check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(StudentLicenseCheck, self).__init__(name='Student License Check', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Check Maya Student License')

    def check(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return True

        return not mayautils.file_has_student_line(filename=scene_path)

    def fix(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return

        mayautils.clean_student_line(filename=scene_path)
        self._valid_check = not mayautils.file_has_student_line(filename=scene_path)
        valid = super(StudentLicenseCheck, self).fix()
        if not valid:
            sys.solstice.logger.warning('Impossible to fix Maya Student License Check')
            return False

        return True


class CleanOldPluginsCheck(check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(CleanOldPluginsCheck, self).__init__(name='Clean Old Plugins', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Clean Old Plugins Nodes')

    def check(self):
        old_plugins = cmds.unknownPlugin(query=True, list=True)
        if old_plugins and type(old_plugins) == list:
            return not len(old_plugins) > 0

        return True

    def fix(self):
        old_plugins = cmds.unknownPlugin(query=True, list=True)
        if old_plugins and type(old_plugins) == list:
            for plugin in old_plugins:
                sys.solstice.logger.info('Removing {} old plugin ...'.format(plugin))
                cmds.unknownPlugin(plugin, remove=True)

        cmds.SaveScene()

        old_plugins = cmds.unknownPlugin(query=True, list=True)
        if old_plugins and type(old_plugins) == list:
            return not len(old_plugins) > 0

        return True


class CleanUnknownNodesCheck(check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(CleanUnknownNodesCheck, self).__init__(name='Clean Unknown Nodes', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Clean Unknown Nodes')

    def check(self):
        unknown_nodes = cmds.ls(type='unknown')
        if unknown_nodes and type(unknown_nodes) == list:
            return not len(unknown_nodes) > 0

        return True

    def fix(self):
        unknown_nodes = cmds.unknownPlugin(query=True, list=True)
        if unknown_nodes and type(unknown_nodes) == list:
            for i in unknown_nodes:
                if cmds.objExists(i):
                    if not cmds.referenceQuery(i, isNodeReferenced=True):
                        sys.solstice.logger.info('Removing {} unknown node ...'.format(i))
                        cmds.delete(i)

        cmds.SaveScene()

        unknown_nodes = cmds.unknownPlugin(query=True, list=True)
        if unknown_nodes and type(unknown_nodes) == list:
            return not len(unknown_nodes) > 0

        return True
