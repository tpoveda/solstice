#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_launcher.py
# by Tomas Poveda
# Module that contains Solstice Config definition
# ______________________________________________________________________
# ==================================================================="""

import os
import platform
import subprocess

from PySide.QtCore import *

import solstice_launcher_utils as utils


class SolsticeConfig(QSettings, object):
    """
    Configuration file for Solstice Short Film
    """

    # Sections
    EXECUTABLES = 'executables'
    ENVIRONMENTS = 'environments'

    def __init__(self, filename, window, console):
        super(SolsticeConfig, self).__init__(str(filename), QSettings.IniFormat, window)
        self.config_file = filename
        console.write('Solstice Configuration File: {}'.format(filename))

    def edit(self):
        """
        Edit file with default OS application
        """

        if platform.system().lower() == 'windows':
            os.startfile(str(self.config_file))
        else:
            if platform.system().lower() == 'darwin':
                call = 'open'
            else:
                call = 'xdg-open'
            subprocess.call(call, self.config_file)


def create_config(console, window, dcc_install_path, config_file=None):
    """
    Construct the Solstice configuration object from necessary elements
    """

    if config_file is None:
        config_file = utils.get_system_config_directory(console=console)
    config = SolsticeConfig(filename=config_file, window=window, console=console)

    if not dcc_install_path:
        console.write('Dcc Location not found: Solstice Launcher will not launch DCC!')
        return config

    # for item in application_versions.items():
    config.setValue('executable', os.path.abspath(dcc_install_path))

    return config
