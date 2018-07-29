#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_studentcheck.py
# by Tomas Poveda
# Checks for student license and fix the problem if necessary
# ______________________________________________________________________
# ==================================================================="""

import os

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_checks import solstice_check
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

        valid = super(StudentLicenseCheck, self).fix()
        if not valid:
            sp.logger.warning('Impossible to fix Maya Student License Check')