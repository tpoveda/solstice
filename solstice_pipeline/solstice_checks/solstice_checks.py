#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_checks.py
# by Tomas Poveda
# Module that contains generic checks
# ______________________________________________________________________
# ==================================================================="""

import os

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_checks import solstice_check
from solstice_pipeline.solstice_utils import solstice_maya_utils


class StudentLicenseCheck(solstice_check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(StudentLicenseCheck, self).__init__(name='Student License Check', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Check Maya Student License')

    def check(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return True

        return not solstice_maya_utils.file_has_student_line(filename=scene_path)

    def fix(self):
        scene_path = cmds.file(query=True, sn=True)
        if scene_path is None or not os.path.exists(scene_path):
            return

        solstice_maya_utils.clean_student_line(filename=scene_path)
        self._valid_check = not solstice_maya_utils.file_has_student_line(filename=scene_path)
        valid = super(StudentLicenseCheck, self).fix()
        if not valid:
            sp.logger.warning('Impossible to fix Maya Student License Check')
            return False

        return True


class CleanOldPluginsCheck(solstice_check.SanityCheckTask, object):
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
                sp.logger.info('Removing {} old plugin ...'.format(plugin))
                cmds.unknownPlugin(plugin, remove=True)

        cmds.SaveScene()

        old_plugins = cmds.unknownPlugin(query=True, list=True)
        if old_plugins and type(old_plugins) == list:
            return not len(old_plugins) > 0

        return True


class CleanUnknownNodesCheck(solstice_check.SanityCheckTask, object):
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
                        sp.logger.info('Removing {} unknown node ...'.format(i))
                        cmds.delete(i)

        cmds.SaveScene()

        unknown_nodes = cmds.unknownPlugin(query=True, list=True)
        if unknown_nodes and type(unknown_nodes) == list:
            return not len(unknown_nodes) > 0

        return True
