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

import webbrowser
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from artellapipe.core import project as artella_project

import solstice
from solstice.launcher import tray


class Solstice(artella_project.ArtellaProject):

    PROJECT_PATH = solstice.get_project_path()
    TRAY_CLASS = tray.SolsticeTray
    PROJECT_CONFIG_PATH = solstice.get_project_config_path()
    PROJECT_SHELF_FILE_PATH = solstice.get_project_shelf_path()
    PROJECT_MENU_FILE_PATH = solstice.get_project_menu_path()

    def __init__(self, resource=None):

        self._project_url = None
        self._documentation_url = None
        self._emails = list()

        super(Solstice, self).__init__(resource=resource)

    def init_config(self):
        super(Solstice, self).init_config()

        project_config_data = self.get_config_data()
        if not project_config_data:
            return

        self._project_url = project_config_data.get('PROJECT_URL', None)
        self._documentation_url = project_config_data.get('PROJECT_DOCUMENTATION_URL', None)
        self._emails = project_config_data.get('EMAILS', list())

    @property
    def project_url(self):
        """
        Returns URL to official Plot Twist web page
        :return: str
        """

        return self._project_url

    @property
    def documentation_url(self):
        """
        Returns URL where Plot Twist documentation is stored
        :return: str
        """

        return self._documentation_url

    @property
    def emails(self):
        """
        Returns list of emails that will be used when sending an email
        :return: list(str)
        """

        return self._emails

    def open_webpage(self):
        """
        Opens Plot Twist official web page in browser
        """

        if not self._project_url:
            return

        webbrowser.open(self._project_url)

    def open_documentation(self):
        """
        Opens Plot Twist documentation web page in browser
        """

        if not self._documentation_url:
            return

        webbrowser.open(self._documentation_url)

    def send_email(self, title=None):
        """
        Opens email application with proper info
        """

        if not title:
            title = self.name.title()

        webbrowser.open("mailto:%s?subject=%s" % (','.join(self._emails), quote(title)))
