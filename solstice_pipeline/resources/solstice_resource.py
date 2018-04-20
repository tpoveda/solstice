#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_resource.py
# by Tomas Poveda
# Module that defines a base class to load resources
# ______________________________________________________________________
# ==================================================================="""

import os

from Qt.QtGui import *

from solstice_gui import solstice_pixmap


def get(*args):
    """
    Returns path for the given resource name
    :param args: str, name of the source to retrieve path of
    :return: str
    """

    return Resource().get(*args)


def icon(*args, **kwargs):
    """
    Returns icon for the given resource name
    :param name: str, name of the icon
    :param extension: str, extension of the icon
    :param color: QColor, color of the icon
    :return: QIcon
    """

    return Resource().icon(*args, **kwargs)


def pixmap(*args, **kwargs):
    """
    Returns QPixmap for the given resource name
    :param name: str, name of the pixmap
    :param category: str, category of the pixmap
    :param extension: str, extension of the pixmap
    :param color: QColor, color of the pixmap
    :return: QPixmap
    """

    return Resource().pixmap(*args, **kwargs)


class Resource(object):

    RESOURCES_FOLDER = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, *args):
        dirname = ''
        if args:
            dirname = os.path.join(*args)
        if os.path.isfile(dirname):
            dirname = os.path.dirname(dirname)
        self._dirname = dirname or self.RESOURCES_FOLDER

    def dirname(self):
        """
        Returns absolute path to the resource
        :return: str
        """

        return self._dirname

    def get(self, *args):
        """
        Returns the resource path with the given paths
        :param args: str, resource name
        :return: str
        """

        return os.path.join(self.dirname(), *args)

    def icon(self, name, extension='png', color=None):
        """
        Returns a QIcon object from the given resource name
        :param name: str, name of the icon
        :param extension: str, extension of the icon
        :param color: QColor, color of the icon
        :return: QIcon
        """

        p = self.pixmap(name=name, category='icons', extension=extension, color=color)
        return QIcon(p)

    def pixmap(self, name, category='images', extension='png', color=None):
        """
        Return a QPixmap object from the given resource anme
        :param name: str, name of the pixmap
        :param category: str, category of the pixmap
        :param extension: str, extension of the pixmap
        :param color: QColor, color of the pixmap
        :return: QPixmap
        """

        path = self.get(category, name + '.' + extension)
        p = solstice_pixmap.Pixmap(path)
        if color:
            p.set_color(new_color=color)

        return p


