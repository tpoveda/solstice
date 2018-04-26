#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_maya.py
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


def launch_maya(exec_, args, console):
    """
    Launches Maya application with a proper configuration
    """

    if not exec_:
        console.write_error('Solstice Launcher could not find Maya executable, please contact TD!')
        return

    watched = utils.WatchFile()
    cmd = [exec_] if args.file is None else [exec_, args.file]
    cmd.extend(['-hideConsole', '-log', watched.path])
    if args.debug:
        cmd.append('-noAutoloadPlugins')

    console.write_ok('Launching Maya with commands: {}'.format(cmd))
    QCoreApplication.processEvents()

    os.environ['TEST'] = 'TEST'

    maya = subprocess.Popen([exec_])

    # while True:
    #     time.sleep(2)
    #
    #     maya.poll()
    #     watched.check()
    #     if maya.returncode is not None:
    #         if not maya.returncode == 0:
    #             maya = subprocess.Popen(cmd)
    #         else:
    #             watched.stop()
    #             break

