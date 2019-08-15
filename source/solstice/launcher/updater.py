#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Plot Twist Artella updater
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpPyUtils import path as path_utils

from artellalauncher.core import defines, updater as core_updater

import solstice


def get_updater_config_path():
    """
    Returns path where default Artella updater config is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(solstice.get_project_path(), defines.ARTELLA_UPDATER_CONFIG_FILE_NAME))


class SolsticeUpdater(core_updater.ArtellaUpdater, object):

    UPDATER_CONFIG_PATH = get_updater_config_path()

    def __init__(self, launcher, project, parent=None):
        super(SolsticeUpdater, self).__init__(launcher=launcher, project=project, parent=parent)
