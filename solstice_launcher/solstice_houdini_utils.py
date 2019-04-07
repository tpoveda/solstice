#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_houdini_utils.py
# by Tomas Poveda
# Module that contains Solstice utilities functions related with Houdini
# ______________________________________________________________________
# ==================================================================="""

import subprocess
import os
import time

from PySide.QtCore import *

import solstice_launcher_utils as utils


def launch_houdini(exec_, console):
    """
    Launches Maya application with a proper configuration
    """

    if not exec_:
        console.write_error('Solstice Launcher could not find Houdini executable, please contact TD!')
        return

    watched = utils.WatchFile()
    cmd = [exec_]

    cmd.extend(['-hideConsole', '-log', watched.path])

    console.write_ok('Launching Houdini with commands: {}'.format(cmd))
    QCoreApplication.processEvents()

    houdini = subprocess.Popen([exec_])
