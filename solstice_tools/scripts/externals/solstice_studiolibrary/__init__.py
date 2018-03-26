# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import os
import sys


__version__ = "2.4.0b2"

_resource = None


PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH)
PACKAGES_PATH = os.path.join(DIRNAME, "packages")
RESOURCE_PATH = os.path.join(DIRNAME, "resource")
HELP_URL = "http://www.solstice_studiolibrary.com"


def version():
    """
    Return the current version of the Studio Library

    :rtype: str
    """
    return __version__


def resource():
    """
    Return a resource object for getting content from the resource folder.

    :rtype: solstice_studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = solstice_studioqt.Resource(RESOURCE_PATH)

    return _resource


def setup(path):
    """
    Setup the packages that have been decoupled from the Studio Library.

    :param path: The folder location that contains all the packages.
    :type path: str

    :rtype: None
    """
    if os.path.exists(path) and path not in sys.path:
        sys.path.append(path)


setup(PACKAGES_PATH)


import solstice_studioqt

from solstice_studiolibrary.cmds import *
from solstice_studiolibrary.database import Database
from solstice_studiolibrary.libraryitem import LibraryItem
from solstice_studiolibrary.librarywidget import LibraryWidget
from solstice_studiolibrary.main import main

import solstice_studiolibrary.folderitem

# Wrapping the following functions for convenience
app = solstice_studioqt.app
