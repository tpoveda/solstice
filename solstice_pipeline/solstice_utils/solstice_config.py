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
import traceback
import subprocess
import ConfigParser

from solstice_pipeline.solstice_utils import solstice_python_utils as utils


class SolsticeConfig(ConfigParser.RawConfigParser, object):
    """
    Configuration file for Solstice Short Film
    """

    EXCLUDE_PATTERNS = ['__*', '*.']
    ICON_EXTENSIONS = ['xpm', 'png', 'bmp', 'jpeg']

    def __init__(self, app_name, *args, **kwargs):
        super(SolsticeConfig, self).__init__(*args, **kwargs)

        self._app_name = app_name.replace(' ', '_').lower()
        self.config_file = os.path.join(utils.get_system_config_directory(), 'solstice_pipeline', self._app_name, 'config.ini')

        print('{0}: Solstice Configuration File: {1}'.format(self._app_name, self.config_file))
        try:
            self.readfp(open(self.config_file, 'r'))
            print('{0}: Solstice Configuration File read successfully!'.format(self._app_name))
        except Exception:
            try:
                print('{0}: Solstice Configuration file not found! Creating it...'.format(self._app_name))
                self._create()
            except Exception as e:
                print('{0}: Error reading Solstice Configuration file: {} | {}'.format(e, traceback.format_exc()))

    @property
    def app_name(self):
        return self._app_name

    def _create(self):
        """
        If Solstice configuration file is not already created we create it
        """

        print('Initializing {0} Settings, creating configuration file: {1}\n'.format(self._app_name, self.config_file))

        self.add_section(self._app_name)

        if not os.path.exists(os.path.dirname(self.config_file)):
            try:
                print('Creating Settings Folder: {}'.format(os.path.dirname(self.config_file)))
                original_umask = os.umask(0)
                os.makedirs(os.path.dirname(self.config_file), 0770)
            finally:
                os.umask(original_umask)
        f = open(self.config_file, 'w')
        f.close()
        self.update()

        print('{0} has successfully created a new configuration file at: {1}\n'.format(self._app_name, str(self.config_file)))

    def update(self):
        with open(self.config_file, 'wb') as f:
            self.write(f)

    def get(self, option, section=None):

        if not section:
            section = self._app_name

        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except ConfigParser.NoOptionError:
            return ''

    def get_list(self, option, section=None):
        """
        Convert string value to list object
        """

        if not section:
            section = self._app_name

        if self.has_option(section, option):
            return self.get(section=section, option=option).replace(' ', '').split(',')
        else:
            raise KeyError('{0} with {1} does not exist!'.format(section, option))

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


def create_config(app_name):
    """
    Construct the Solstice configuration object from necessary elements
    """

    config = SolsticeConfig(app_name, allow_no_value=True)

    return config