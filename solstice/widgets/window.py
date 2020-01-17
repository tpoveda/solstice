#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base wrapper classes to create DCC windows for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from tpQtLib.core import dragger

import artellapipe.register
from artellapipe.widgets import window
from artellapipe.libs.kitsu.widgets import userinfo


class SolsticeWindowDragger(dragger.WindowDragger, object):
    def __init__(self, parent=None, on_close=None):
        self._user_info = None
        super(SolsticeWindowDragger, self).__init__(parent=parent, on_close=on_close)

    def set_project(self, project):
        pass
        if self._user_info:
            self._user_info.set_project(project)
        else:
            self._user_info = userinfo.KitsuUserInfo(project=project)
            self.buttons_layout.insertWidget(0, self._user_info)

    def try_kitsu_login(self):
        """
        Function that tries to login into Kitsu with stored credentials
        :return: bool
        """

        if not self._user_info:
            return False

        valid_login = self._user_info.try_kitsu_login()
        if valid_login:
            return True

        return False


class SolsticeWindow(window.ArtellaWindow, object):

    DRAGGER_CLASS = SolsticeWindowDragger

    def __init__(self, *args, **kwargs):
        super(SolsticeWindow, self).__init__(*args, **kwargs)

        if not self._tool:
            return

        kitsu_login = self._tool.config.get('kitsu_login', default=True)
        if kitsu_login:
            self._dragger.set_project(self._project)

    def try_kitsu_login(self):
        """
        Function that tries to login into Kitsu with stored credentials
        :return: bool
        """

        if not self._tool:
            return

        kitsu_login = self._tool.config.get('kitsu_login', default=True)
        if kitsu_login:
            return self._dragger.try_kitsu_login()


artellapipe.register.register_class('Window', SolsticeWindow)
