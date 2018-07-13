#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_artella_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities related with Artella
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import subprocess
import logging
import psutil

from PySide.QtGui import *
from PySide.QtCore import *


artella_maya_plugin_name = 'Artella.py'
artella_app_name = 'lifecycler'

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def update_artella_paths(console):
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    artella_folder = get_artella_data_folder()

    console.write('Updating Artella paths from: {0}'.format(artella_folder))
    for subdir, dirs, files in os.walk(artella_folder):
        if subdir not in sys.path:
            console.write('Adding Artella path: {0}'.format(subdir))
            sys.path.append(subdir)


def get_artella_data_folder():
    """
    Returns last version Artella folder installation
    :return: str
    """

    # TODO: This should not work in MAC, find a cross-platform way of doing this
    artella_folder = os.path.join(os.getenv('PROGRAMDATA'), 'Artella')

    artella_app_version = None
    version_file = os.path.join(artella_folder, 'version_to_run_next')
    if os.path.isfile(version_file):
        with open(version_file) as f:
            artella_app_version = f.readline()

    if artella_app_version is not None:
        artella_folder = os.path.join(artella_folder, artella_app_version)
    else:
        artella_folder = [os.path.join(artella_folder, name) for name in os.listdir(artella_folder) if os.path.isdir(os.path.join(artella_folder, name)) and name != 'ui']
        if len(artella_folder) == 1:
            artella_folder = artella_folder[0]
        else:
            logger.info('Artella folder not found!')

    logger.info('ARTELLA FOLDER: {}'.format(artella_folder))
    if not os.path.exists(artella_folder):
        QMessageBox.information(None, 'Artella App Folder {} does not exists! Solstice Launcher will continue but maybe will not as it should. Please contact Solstice TD to check this problem!')

    return artella_folder


def get_artella_program_folder():
    """
    Returns folder where Artella shortcuts are located
    :return: str
    """

    return os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Artella')


def get_artella_launch_shortcut():
    """
    Returns path where Launch Artella shortcut is located
    :return: str
    """

    return os.path.join(get_artella_program_folder(), 'Launch Artella.lnk')


def get_artella_plugins_folder():
    """
    Returns folder where Artelle stores its plugins
    :return: str
    """

    return os.path.join(get_artella_data_folder(), 'plugins')


def get_artella_dcc_plugin(dcc='maya'):
    """
    Gets Artella DCC plugin depending of the given dcc string
    :param dcc: str, "maya" or "nuke"
    :return: str
    """

    artella_folder = get_artella_data_folder()
    return os.path.join(get_artella_plugins_folder(), dcc)


def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    artella_folder = os.path.dirname(get_artella_data_folder())
    return os.path.join(artella_folder, artella_app_name)


def launch_artella_app(console):
    """
    Executes Artella App
    """

    # TODO: This should not work in MAC, find a cross-platform way of doing this
    if os.name == 'mac':
        console.write('Launch Artella App: does not supports MAC yet')
        artella_app_file = get_artella_app() + '.bundle'
    else:
        #  Executing Artella executable directly does not work
        # artella_app_file = get_artella_app() + '.exe'
        artella_app_file = get_artella_launch_shortcut()

    artella_app_file = artella_app_file
    console.write('Artella App File: {0}'.format(artella_app_file))

    if os.path.isfile(artella_app_file):
        logger.info('Launching Artella App ...')
        logger.info('Artella App File: {0}'.format(artella_app_file))
        os.startfile(artella_app_file.replace('\\', '//'))


def close_all_artella_app_processes(console):
    """
    Closes all Artella app (lifecycler.exe) processes
    :return:
    """

    for proc in psutil.process_iter():
        if proc.name() == artella_app_name + '.exe':
            logger.debug('Killing Artella App process: {}'.format(proc.name()))
            console.write('Killing Artella App process: {}'.format(proc.name()))
            proc.kill()
