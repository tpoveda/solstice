#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella launcher implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpPyUtils import path as path_utils

from artellalauncher.core import defines, launcher

import solstice
from solstice.launcher import updater, dccselector


def get_launcher_config_path():
    """
    Returns path where default Artella project config is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(solstice.get_project_path(), defines.ARTELLA_LAUNCHER_CONFIG_FILE_NAME))


class SolsticeLauncher(launcher.ArtellaLauncher, object):

    DCC_SELECTOR_CLASS = dccselector.SolsticeDCCSelector
    UPDATER_CLASS = updater.SolsticeUpdater
    LAUNCHER_CONFIG_PATH = get_launcher_config_path()

    def __init__(self, project, resource):
        super(SolsticeLauncher, self).__init__(project=project, resource=resource)


