#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

DEF_MAYA_EXECUTABLE = 'maya.exe'
DEF_HOUDINI_EXECUTABLE = 'houdini.exe'


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


def get_maya_installation(maya_version):
    """
    Returns the installation folder of Maya
    :return:
    """
    versions = dict()

    maya_location = None
    if platform.system().lower() == 'windows':
        try:
            from _winreg import *
            a_reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            a_key = OpenKey(a_reg, r"SOFTWARE\Autodesk\Maya\{}\Setup\InstallPath".format(maya_version))
            value = QueryValueEx(a_key, 'MAYA_INSTALL_LOCATION')
            maya_location = value[0]
        except Exception:
            maya_location = os.getenv('MAYA_LOCATION')
            if not maya_location:
                path = 'C:/Program Files/Autodesk/Maya{}'.format(maya_version)
                if os.path.exists(path):
                    maya_location = path

    if maya_location is None or not os.path.exists(maya_location):
        # QMessageBox.information(None, 'Maya location not found', 'Solstice Launcher will not launch Maya!')
        return None

    maya_executable = get_maya_executables_from_installation_path(maya_location)

    if maya_executable is None or not os.path.isfile(maya_executable):
        maya_executable = str(QFileDialog.getOpenFileName(None, 'Select Maya {} installation'.format(maya_version))[0])
        if not os.path.isfile(maya_executable):
            return None
    versions['{}'.format(maya_version)] = maya_executable

    # We are not interested in supporting multiple Maya versions
    # return versions

    return maya_executable


def get_houdini_executables_from_installation_path(installation_path):
    """
    Returns Houdini executable from its installation path
    :param installation_path: str
    """

    if os.path.exists(installation_path):
        bin_path = os.path.join(installation_path, 'bin')

        if not os.path.exists(bin_path):
            return None
        houdini_files = os.listdir(bin_path)
        if DEF_HOUDINI_EXECUTABLE in houdini_files:
            return os.path.join(bin_path, DEF_HOUDINI_EXECUTABLE)

    return None


def get_nuke_executables_from_installation_path(installation_path):
    """
    Returns Nuke executable from its installation path
    :param installation_path: str
    """

    if os.path.exists(installation_path):
        nuke_files = os.listdir(installation_path)
        houdini_ex = os.path.basename(installation_path).split('v')[0]+'.exe'
        if houdini_ex in nuke_files:
            return os.path.join(installation_path, houdini_ex)

    return None



def get_houdini_installation():
    """
    Returns the installation folder of Houdini
    :return:
    """

    if platform.system().lower() == 'windows':
        try:
            from _winreg import *
            a_reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            a_key = OpenKey(a_reg, r"SOFTWARE\Side Effects Software\Houdini 17.5.173")
            value = QueryValueEx(a_key, 'InstallPath')
            houdini_location = value[0]
        except Exception:
            houdini_location = None

        if houdini_location is None or not os.path.exists(houdini_location):
            # QMessageBox.information(None, 'Houdini 17.5.173 location not found', 'Solstice Launcher will not launch Houdini!')
            return None

        houdini_executable = get_houdini_executables_from_installation_path(houdini_location)

        if houdini_executable is None or not os.path.isfile(houdini_executable):
            # houdini_executable = str(QFileDialog.getOpenFileName(None, 'Select Houdini 17.5.173 executable')[0])
            # if not os.path.isfile(houdini_executable):
            #     return None
            return None

        return houdini_executable


def get_nuke_installation():
    """
    Returns the installation folder of Nuke
    :return:
    """

    if platform.system().lower() == 'windows':
        nuke_path = os.environ.get('SOLSTICE_NUKE', None)
        if nuke_path is None:
            nuke_path = 'C://Program Files//Nuke11.3v3'

        if not os.path.exists(nuke_path):
            return

        nuke_executable = get_nuke_executables_from_installation_path(nuke_path)
        if nuke_executable is None or not os.path.isfile(nuke_executable):
            # houdini_executable = str(QFileDialog.getOpenFileName(None, 'Select Nuke executable')[0])
            # if not os.path.isfile(houdini_executable):
            return None

        return nuke_executable


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
            self.current_line = len(lines)

    def stop(self):
        os.remove(self.path)
