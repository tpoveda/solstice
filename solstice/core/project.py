#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Artella project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpDcc.libs.python import timedate, osplatform

import artellapipe
from artellapipe.core import project as artella_project


class Solstice(artella_project.ArtellaProject, object):

    def __init__(self):
        super(Solstice, self).__init__(name='Solstice')

    def notify(self, title, msg):
        """
        Overrides base ArtellaProject notify function
        :param title: str
        :param msg: str
        """

        super(Solstice, self).notify(title=title, msg=msg)

        if artellapipe.SlackMgr().slack_is_available():
            artellapipe.SlackMgr().post_message(
                '{} | {} | {} : {}'.format(
                    timedate.get_current_time(), osplatform.get_user(True), title, msg))

    def get_toolsets_paths(self):
        """
        Overrides base ArtellaProject get_toolsets_paths
        Returns path where project toolsets are located
        :return: list(str)
        """

        import solstice.toolsets

        return [os.path.dirname(os.path.abspath(solstice.toolsets.__file__))]

    def get_resources_paths(self):
        """
        Overrides base ArtellaProject get_resources_paths
        Returns path where project resources are located
        :return: dict(str, str)
        """

        resources_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
        return {
            'project': resources_path,
            'shelf': os.path.join(resources_path, 'icons', 'shelf')
        }
