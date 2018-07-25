#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_updater.py
# by Tomas Poveda
# Module that contains necessary functionality to update Solstice Tools
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import tempfile
import json
import time

from PySide.QtGui import *
from PySide.QtCore import *

import solstice_download_utils as utils

numbers = re.compile('\d+')


class SolsticeTools():
    file = 'solstice_pipeline.zip'
    repo_url = 'http://cgart3d.com/solstice_pipeline/'
    setup_json = 'setup.json'
    setup_file = '{}{}'.format(repo_url, setup_json)

    @staticmethod
    def set_installation_path():
        """
        Set Solstice Tools installation path
        :return: str
        """

        selected_dir = QFileDialog.getExistingDirectory()
        if not os.path.exists(selected_dir):
            new_dir = SolsticeTools.get_installation_path()
            print('Selected Installation Folder: {0} does not exists! Installing in default path: {1}'.format(selected_dir, new_dir))
            selected_dir = new_dir

        return os.path.abspath(selected_dir)

    @staticmethod
    def get_default_installation_path(fullpath=False):
        """
        Return Default Solstice Tools installation path
        :return: str
        """

        maya_path = os.path.join(os.path.expanduser("~/"), 'maya')
        if not os.path.exists(maya_path):
            maya_path = os.path.join(os.path.expanduser("~/Documents"), 'maya')
        if not os.path.exists(maya_path):
            return None
        if fullpath:
            maya_path = os.path.join(maya_path, 'solstice_pipeline')

        return maya_path

    @staticmethod
    def get_installation_path(config=None):
        """
        Return Solstice Tools installation path
        :return: str
        """

        try:
            if config:
                install_path = config.value('solstice_pipeline_install')
            else:
                install_path = SolsticeTools.get_default_installation_path()
                config.setValue('solstice_pipeline_install', install_path)
        except Exception:
            install_path = SolsticeTools.get_default_installation_path()
            config.setValue('solstice_pipeline_install', install_path)

        return install_path


class SolsticeUpdater(QWidget, object):
    def __init__(self, config, parent=None):
        super(SolsticeUpdater, self).__init__(parent=parent)

        self.config = config

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self._progress_bar = QProgressBar()
        main_layout.addWidget(self._progress_bar)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }")

        self._progress_text = QLabel('Downloading Solstice Tools ...')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        main_layout.addWidget(self._progress_text)


def get_version(s):
    """
    Look for the last sequence of number(s) in a string and increment
    """

    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr
    return None


def check_current_solstice_tools_version(config, console):
    """
    Returns the current installed Sosltice Tools version
    :return: str
    """

    install_path = SolsticeTools.get_installation_path(config=config)
    solstice_tools_path = os.path.join(install_path, 'solstice_pipeline', 'settings.json')
    if os.path.isfile(solstice_tools_path):
        with open(solstice_tools_path, 'r') as fl:
            install_info = json.loads(fl.read())
        install_version = install_info.get('version')
        if not install_info:
            console.write_error('Installed version impossible to get ...!')

            return None

        console.write_ok('Current installed version: {0}'.format(install_version))

        installed_version = get_version(install_version)
        return installed_version
    return None


def check_solstice_tools_version(console, updater, get_versions=False):
    """
    Checks the current installed version, returns True if you you do not have
    the last Sosltice Tools installed version or False otherwise
    :param console:
    :param updater:
    :param get_versions:
    :return:
    """

    # Find a way to delete this folder when the process is completed
    temp_path = tempfile.mkdtemp()
    install_path = SolsticeTools.get_installation_path(config=updater.config)
    if install_path is None or not os.path.exists(install_path):
        console.write_error('Installation path {0} does not exists! Check that Maya is installed in your system!'.format(install_path))
        return
    else:
        console.write('Installation Path detected: {0}'.format(install_path))

    setup_path = os.path.join(temp_path, SolsticeTools.setup_json)
    setup_file = SolsticeTools.setup_file

    console.write('Solstice Tools Setup File: {0}'.format(setup_file))
    console.write('Solstice Tools Setup Path: {0}'.format(setup_path))

    if not utils.download_file(filename=setup_file, destination=setup_path, console=console, updater=updater):
        console.write_error('setup.json is not accessible! Maybe server is down or your internet connection is down! Contact TD please!')
        return

    console.write('{0} file downloaded successfully on {1}'.format(setup_file, setup_path))

    with open(setup_path, 'r') as fl:
        setup_info = json.loads(fl.read())

    last_version = setup_info.get('lastVersion')
    if not last_version:
        console.write_error('setup.json is not accessible! Maybe server is down or your internet connection is down! Contact TD please!')
        return
    last_version_value = get_version(last_version)
    console.write_ok('Last Solstice Tools deployed version is {0}'.format(last_version))
    solstice_tools_path = os.path.join(install_path, 'solstice_pipeline', 'settings.json')
    console.write('Checking current Solstice Tools installed version on {0}'.format(solstice_tools_path))

    try:
        if os.path.isfile(solstice_tools_path):
            with open(solstice_tools_path, 'r') as fl:
                install_info = json.loads(fl.read())
            install_version = install_info.get('version')
            if not install_info:
                console.write_error('Installed version impossible to get ... Please contact TD!')
                return
            console.write_ok('Current installed version: {0}'.format(install_version))

            installed_version = get_version(install_version)

            if installed_version and last_version_value <= installed_version:
                console.write_ok('Current installed tools {0} are up-to-date (version in server {1})!'.format(install_version, last_version))

                if get_versions:
                    return last_version, installed_version, False
                else:
                    return False
            else:
                if get_versions:
                    return last_version, installed_version, True
                else:
                    return True
        else:
            if get_versions:
                return last_version, None, True
            else:
                return True
    except Exception as e:
        console.write_error('Error while retrieving Solstice Tools version. Check your Internet connection or contact Solstice TD!')
        console.write_error(str(e))
        return False


def update_solstice_tools(console, updater):
    """
    Update Solstice Tools to the last version
    """

    try:
        temp_path = tempfile.mkdtemp()

        last_version, installed_version, need_to_update = check_solstice_tools_version(console=console, updater=updater, get_versions=True)

        if need_to_update:
            install_path = SolsticeTools.get_installation_path(config=updater.config)
            if install_path is None or not os.path.exists(install_path):
                console.write_error('Install path {0} does not exists!'.format(install_path))
                return
            else:
                console.write('Install Path detected: {0}'.format(install_path))

            QCoreApplication.processEvents()

            console.write('=' * 15)
            console.write_ok('Current installed Solstice Tools are outdated {0}! Installing new tools ... {1}!'.format(installed_version, last_version))
            console.write('=' * 15)

            QCoreApplication.processEvents()

            solstice_tools_zip_file = '{}{}/{}'.format(SolsticeTools.repo_url, last_version, SolsticeTools.file)
            solstice_tools_install_path = os.path.join(temp_path, last_version, SolsticeTools.file)
            console.write('Solstice Pipeline File: {0}'.format(solstice_tools_zip_file))
            console.write('Solstice Pipeline Install Path: {0}'.format(solstice_tools_install_path))

            QCoreApplication.processEvents()
            if not utils.download_file(filename=solstice_tools_zip_file, destination=solstice_tools_install_path, console=console, updater=updater):
                console.write_error('{0} is not accessible! Maybe server is down or your internet connection is down! Contact TD please!'.format(SolsticeTools.file))
                return
            console.write_ok('Installing Solstice Pipeline on: {0}'.format(install_path))
            QCoreApplication.processEvents()

            time.sleep(1)

            updater._progress_text.setText('Installing Solstice Pipeline ...')
            QCoreApplication.processEvents()
            utils.unzip_file(filename=solstice_tools_install_path, destination=install_path, console=console, removeSubfolders=['solstice_pipeline'])

            console.write('=' * 15)
            console.write_ok('Soltice Pipeline {0} installed successfully!'.format(last_version))
            console.write('=' * 15)
            QCoreApplication.processEvents()

            return True
    except Exception:
        return False
