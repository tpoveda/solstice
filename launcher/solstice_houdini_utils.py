#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_houdini_utils.py
# by Tomas Poveda
# Module that contains Solstice utilities functions related with Houdini
# ______________________________________________________________________
# ==================================================================="""

import subprocess

from PySide.QtCore import *


def launch_houdini(exec_, console, script_path, houdini_path, bootstrap):
    """
    Launches Maya application with a proper configuration
    """

    if not exec_:
        console.write_error('Solstice Launcher could not find Houdini executable, please contact TD!')
        return

    cmd = [bootstrap]

    cmd.extend([exec_, houdini_path, script_path])

    QCoreApplication.processEvents()

    subprocess.Popen(cmd)


    # cmd = [exec_]
    #
    # cmd.extend(['waitforui', script_path])
    #
    # console.write_ok('Launching Houdini with commands: {}'.format(cmd))
    # QCoreApplication.processEvents()
    #
    # houdini = subprocess.Popen(cmd)
