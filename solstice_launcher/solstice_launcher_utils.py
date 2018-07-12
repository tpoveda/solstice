#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_launcher_utils.py
# by Tomas Poveda
# Utilities functions for Solstice Launcher
# ______________________________________________________________________
# ==================================================================="""

import os
import platform
import tempfile
import argparse
from pathlib2 import Path

from PySide.QtGui import *
from PySide.QtCore import *

import solstice_updater as updater


DEF_MAYA_PATH_INSTALLATIONS = ['C://Program Files//Autodesk//Maya2017']
DEF_MAYA_EXECUTABLE = 'maya.exe'


def get_system_config_directory(console=None, as_path=False):
    """
    Returns platform specific configuration directory
    """

    if platform.system().lower() == 'windows':
        config_directory = Path(os.getenv('APPDATA') or '~')
    elif platform.system().lower() == 'darwin':
        config_directory = Path('~', 'Library', 'Preferences')
    else:
        config_directory = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config')

    if console:
        console.write('Fetching configruation directory for {}'.format(platform.system()))
        console.write('Getting Installed Solstice Tools version ...')

    if as_path:
        return config_directory.joinpath(Path('solstice_launcher'))
    else:
        return config_directory.joinpath(Path('solstice_launcher/.config'))

    # The configuration file will be shared for new updates
    # last_version = updater.check_current_solstice_tools_version(config=config, console=console)
    #
    # if last_version:
    #     return config_directory.joinpath(Path('solstice_launcher/{0}/.config'.format(last_version)))
    # else:
    #     return config_directory.joinpath(Path('solstice_launcher/.config'))


def get_maya_executables_from_installation_path(installation_path):
    """
    Returns Maya executable from its installation path
    :param installation_path: str
    """

    if os.path.exists(installation_path):
        bin_path = os.path.join(installation_path, 'bin')
        if not os.path.exists(bin_path):
            return None
        maya_files = os.listdir(bin_path)
        if DEF_MAYA_EXECUTABLE in maya_files:
            return os.path.join(bin_path, DEF_MAYA_EXECUTABLE)

    return None


def get_maya_2017_installation():
    """
    Returns the installation folder of Maya
    :return:
    """
    versions = dict()

    if platform.system().lower() == 'windows':
        maya_location = os.getenv('MAYA_LOCATION')
        if not maya_location:
            for path in DEF_MAYA_PATH_INSTALLATIONS:
                if os.path.exists(path):
                    maya_location = path
                    break

    if not os.path.exists(maya_location):
        QMessageBox.information(None, 'Maya location not found! Solstice Launcher will not launch Maya!')
        return None

    maya_executable = get_maya_executables_from_installation_path(maya_location)
    if not os.path.isfile(maya_executable):
        maya_executable = str(QFileDialog.getExistingDirectory(None, 'Select Maya 2017 installation'))
        if not os.path.isfile(maya_executable):
            QMessageBox.information(None, 'Maya location not found! Solstice Launcher will not launch Maya!')
            return None
    versions['2017'] = maya_executable

    # We are not interested in supporting multiple Maya versions
    # return versions

    return maya_executable


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def has_next(gen):
    """
    Check if generator if empty
    :param gen:
    :return:
    """

    try:
        gen.next()
        return True
    except StopIteration:
        return False


def is_package(path):
    """
    Returns True if the given path specifies a Python package or False otherwise
    :param path: str
    :return: bool
    """

    return True if has_next(path.glob('__init__.py')) else False


def get_directories_with_extensions(start, extensions=None):
    """
    Look for directories with  specific extensions in given directory and
    return a list with found directories
    :param start: str
    :param extensions: variant, str || None
    :return: list<str>
    """

    return set([p.parent for ext in extensions for p in start.rglob(ext)])


def flatten_combine_lists(*args):
    """
    Flattens and combines list of lists
    """

    return [p for l in args for p in l]


class WatchFile(object):

    LOGFILE_NAME = 'solstice_launcher'
    LOGFILE_DIR = tempfile.gettempdir()

    def __init__(self):
        self.path = os.path.join(self.LOGFILE_DIR, self.LOGFILE_NAME)
        self.dir, self.file = os.path.split(self.path)
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        self.create()

        self.current_line = 0
        self.current_time = self.time

    def check(self):
        if self.is_modified:
            self.on_change()
            self.current_time = self.time

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def is_modified(self):
        return self.time > self.current_time

    @property
    def time(self):
        if self.exists:
            return os.path.getmtime(self.path)

    def create(self):
        counter = 1
        while self.exists:
            self.path = '{}{}'.format(self.path, counter)
            counter += 1
        open(self.path, 'w').close()

    def on_change(self):
        with open(self.path, 'r') as _:
            lines = _.readlines()
            print(''.join(lines[self.current_line:]))
            self.current_line = len(lines)

    def stop(self):
        os.remove(self.path)
