#!/usr/bin/env python
# # -*- coding: utf-8 -*-
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
import ConfigParser

import solstice_launcher_utils as utils
import solstice_updater as updater


class SolsticeConfig(ConfigParser.RawConfigParser, object):
    """
    Configuration file for Solstice Short Film
    """

    EXCLUDE_PATTERNS = ['__*', '*.']
    ICON_EXTENSIONS = ['xpm', 'png', 'bmp', 'jpeg']

    # Sections
    DEFAULTS = 'defaults'
    EXECUTABLES = 'executables'
    PATTERNS = 'patterns'
    ENVIRONMENTS = 'environments'
    INSTALL = 'installation'

    def __init__(self, config_file, console, *args, **kwargs):
        super(SolsticeConfig, self).__init__(*args, **kwargs)

        self.config_file = config_file
        self._console = console
        console.write('Solstice Configuration File: {}'.format(self.config_file))
        try:
            self.readfp(self.config_file.open('r'))
            console.write('Solstice Configuration File read successfully!')
        except IOError:
            console.write('Solstice Configuration file not found! Creating it...')
            self._create()

    def _create(self):
        """
        If Solstice configuration file is not already created we create it
        """

        self._console.write('Initializing Solstice Launcher, creating configuration file...\n')
        self.add_section(self.DEFAULTS)
        self.add_section(self.PATTERNS)
        self.add_section(self.ENVIRONMENTS)
        self.add_section(self.EXECUTABLES)
        self.add_section(self.INSTALL)
        self.set(self.DEFAULTS, 'executable', None)
        self.set(self.DEFAULTS, 'environment', None)
        self.set(self.PATTERNS, 'exclude', ', '.join(self.EXCLUDE_PATTERNS))
        self.set(self.PATTERNS, 'icon_ext', ', '.join(self.ICON_EXTENSIONS))
        self.set(self.INSTALL, 'install_path', updater.SolsticeTools.get_installation_path())

        self.config_file.parent.mkdir(exist_ok=True)
        self.config_file.touch()
        with self.config_file.open('wb') as f:
            self.write(f)

        self._console.write_ok('Solstice Launcher has successfully created a new configuration file at: {}\n'.format(str(self.config_file)))

    def get(self, section, option):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except ConfigParser.NoOptionError:
            return ''

    def get_list(self, section, option):
        """
        Convert string value to list object
        """

        if self.has_option(section, option):
            return self.get(section, option).replace(' ', '').split(',')
        else:
            raise KeyError('{} with {} does not exist!'.format(section, option))

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


def create_config(console, config_file=None):
    """
    Construct the Solstice configuration object from necessary elements
    """

    if config_file is None:
        config_file = utils.get_system_config_directory(console=console)

    config = SolsticeConfig(config_file, console=console, allow_no_value=True)
    application_versions = utils.get_maya_2017_installation()

    if not application_versions:
        return None

    for item in application_versions.items():
        if not config.has_option(SolsticeConfig.EXECUTABLES, item[0]):
            config.set(SolsticeConfig.EXECUTABLES, item[0], item[1])

    return config
