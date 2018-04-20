#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_environment.py
# by Tomas Poveda
# Module that contains classes to define Maya and system environment
# state for Solstice Maya session
# ______________________________________________________________________
# ==================================================================="""

import os
import site
import collections
from pathlib2 import Path

import solstice_launcher_utils as utils
import solstice_config as cfg

from PySide.QtGui import *
from PySide.QtCore import *


def get_environment_paths(config, env):
    """
    Get environment paths from the given environment variable
    """

    if env is None:
        return config.get(cfg.SolsticeConfig.DEFAULTS, 'environment')

    # Configuration option takes precedence over environment key
    install = None
    if config.has_option(cfg.SolsticeConfig.INSTALL, env):
        install = config.get(cfg.SolsticeConfig.INSTALL, env).replace(' ', '').split(';')

    if config.has_option(cfg.SolsticeConfig.ENVIRONMENTS, env):
        env = config.get(cfg.SolsticeConfig.ENVIRONMENTS, env).replace(' ', '').split(';')
        if install:
            env.append(install)
    else:
        if install:
            env = [install]
        else:
            env = os.getenv(env)
            if env:
                env = env.split(os.pathsep)

    return [i for i in env if i]


class EnvironmentList(collections.MutableSequence):
    """
    Converts system environment
    """
    def __init__(self, environment):
        env = os.getenv(environment)
        self.env = [] if env is None else env.split(os.pathsep)
        self.name = environment

    def __str__(self):
        return '{}'.format(self.env)

    def __repr__(self):
        return '{}({}({}))'.format(self.__class__.__name__, self.name, self.env)

    def __len__(self):
        return len(self.env)

    def __getitem__(self, item):
        return self.env[item]

    def __setitem__(self, index, item):
        self.env[index] = str(item)
        self.update()

    def __delitem__(self, item):
        self.env.remove(str(item))
        self.update()

    def insert(self, index, value):
        self.env.insert(index, str(value))
        self.update()

    def append(self, value):
        if str(value) in self.env:
            return
        else:
            self.env.append(str(value))
        self.update()

    def update(self):
        os.environ[self.name] = os.pathsep.join(self.env)


class MayaEnvironment(object):

    MAYA_SCRIPT_PATH = 'MAYA_SCRIPT_PATH'
    MAYA_PYTHON_PATH = 'PYTHONPATH'
    MAYA_XBMLANG_PATH = 'XBMLANGPATH'
    MAYA_PLUG_IN_PATH = 'MAYA_PLUG_IN_PATH'

    PYTHON, MEL, PLUGIN = 'py', 'mel', 'plug-in'

    def __init__(self, console, paths=None):
        self.paths = paths or []
        self.console = console

        self.script_paths = EnvironmentList(self.MAYA_SCRIPT_PATH)
        self.python_paths = EnvironmentList(self.MAYA_PYTHON_PATH)
        self.xbmlang_paths = EnvironmentList(self.MAYA_XBMLANG_PATH)
        self.plug_in_paths = EnvironmentList(self.MAYA_PLUG_IN_PATH)

        console.write('Creating MayaEnvironment ...')
        console.write('{0} : {1}'.format(self.MAYA_SCRIPT_PATH, self.script_paths))
        console.write('{0} : {1}'.format(self.MAYA_PYTHON_PATH, self.python_paths))
        console.write('{0} : {1}'.format(self.MAYA_XBMLANG_PATH, self.xbmlang_paths))
        console.write('{0} : {1}'.format(self.MAYA_PLUG_IN_PATH, self.plug_in_paths))

        self.exclude_pattern = []
        self.icon_extensions = []

    def is_excluded(self, path, exclude=None):
        """
        Returns if given path is in excluded pattern
        :param path: str
        :param exclude: list
        :return: bool
        """

        for pattern in (exclude or self.exclude_pattern):
            if path.match(pattern):
                return True
            else:
                return False

    def walk(self, root, excluded_paths=[]):
        """
        Loops throug directory
        :param root:  str, root directory to start walking from
        :return: list<str>
        """

        for root, dirs, files in os.walk(str(root), topdown=True):
            dirs_ = list()
            for d in dirs:
                p = Path(d)
                if self.is_excluded(p):
                    continue

                if not utils.is_package(Path(root, str(p))):
                    dirs_.append(str(p))
                yield Path(root, str(p)).resolve()
            dirs[:] = dirs_

    def put_path(self, path):
        """
        Checks where the given environment belong and append it where it should go
        :param path: str
        """

        if utils.is_package(path):
            self.console.write('PYTHON PACKAGE: {}'.format(path))
            self.python_paths.append(path.parent)
            site.addsitedir(str(path.parent))
            xbmdirs = utils.get_directories_with_extensions(path, self.icon_extensions)
            self.xbmlang_paths.extend(xbmdirs)
            return

        if utils.has_next(path.glob('*.' + self.MEL)):
            self.console.write('MEL: {}'.format(str(path)))
            self.script_paths.append(path)

        if utils.has_next(path.glob('*.' + self.PYTHON)):
            self.console.write('PYTHONPATH: {}'.format(str(path)))
            self.python_paths.append(path)
            site.addsitedir(str(path))

        if self.PLUGIN in list(path.iterdir()):
            self.console.write('PLUG-IN: {}'.format(str(path)))
            self.plug_in_paths.append(path)

        for ext in self.icon_extensions:
            if utils.has_next(path.glob('*.' + ext)):
                self.console.write('XBM: {}.'.format(str(path)))
                self.xbmlang_paths.append(path)
                break

    def traverse_path_for_valid_application_paths(self, top_path):
        """
        For every path beneath top path that does not contain the excluded
        pattern look for Python, MEL and images and place them into their
        corresponding system environments
        :param top_path: str
        """

        if type(top_path) is list:
            top_path = top_path[0]

        top_path_ = Path(top_path)
        self.put_path(Path(top_path_))
        for p in self.walk(top_path):
            self.put_path(p)

    @staticmethod
    def build(config, console, env=None, arg_paths=None):
        """
        Generates Maya environment
        """

        maya_env = MayaEnvironment(console=console)
        maya_env.exclude_pattern = config.get_list(cfg.SolsticeConfig.PATTERNS, 'exclude')
        maya_env.icon_extensions = config.get_list(cfg.SolsticeConfig.PATTERNS, 'icon_ext')

        console.write('MayaEnvironment - Excluded patterns: {0}'.format(maya_env.exclude_pattern))
        console.write('MayaEnvironment - Icon Extensions: {0}'.format(maya_env.icon_extensions))
        QCoreApplication.processEvents()

        env = get_environment_paths(config=config, env=env)
        if not env and arg_paths is None:
            return console.write('MayaEnvironment not used! Using Maya factory environment setup!')

        console.write('MayaEnvironment: Maya will launch with addon paths: {}'.format(arg_paths))
        console.write('MayaEnvironment: Maya will launch with environment paths: {}'.format(env))
        QCoreApplication.processEvents()

        if arg_paths:
            arg_paths = arg_paths.split(' ')
        for directory in utils.flatten_combine_lists(env, arg_paths or ''):
            maya_env.traverse_path_for_valid_application_paths(directory)

        console.write_ok('Maya Environment: {}'.format(maya_env))

