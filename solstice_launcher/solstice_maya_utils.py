#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya_utils.py
# by Tomas Poveda
# Module that contains Solstice utilities functions related with Maya
# ______________________________________________________________________
# ==================================================================="""

import subprocess
import os
import time

from PySide.QtGui import *
from PySide.QtCore import *

import solstice_launcher_utils as utils


def launch_maya(exec_, console):
    """
    Launches Maya application with a proper configuration
    """

    if not exec_:
        console.write_error('Solstice Launcher could not find Maya executable, please contact TD!')
        return

    # watched = utils.WatchFile()
    cmd = [exec_]
    # cmd.extend(['-hideConsole', '-log', watched.path])

    console.write_ok('Launching Maya with commands: {}'.format(cmd))
    QCoreApplication.processEvents()

    maya = subprocess.Popen(cmd)
