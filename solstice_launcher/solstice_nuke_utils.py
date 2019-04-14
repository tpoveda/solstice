#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_nuke_utils.py
# by Tomas Poveda
# Module that contains Solstice utilities functions related with Nuke
# ______________________________________________________________________
# ==================================================================="""

import subprocess

from PySide.QtCore import *


def launch_nuke(exec_, console, script_path):
    """
    Launches Maya application with a proper configuration
    """

    if not exec_:
        console.write_error('Solstice Launcher could not find Nuke executable, please contact TD!')
        return

    cmd = [exec_]

    cmd.extend(['--', script_path])

    console.write_ok('Launching Nuke with commands: {}'.format(cmd))
    QCoreApplication.processEvents()

    houdini = subprocess.Popen(cmd)
