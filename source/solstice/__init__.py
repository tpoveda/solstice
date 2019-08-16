#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import inspect

from tpPyUtils import importer, path as path_utils
from tpQtLib.core import resource as resource_utils

import artellapipe as artella
from artellapipe.core import defines as artella_defines

from solstice.core import defines


# =================================================================================

logger = None
resource = None

# =================================================================================


class SolsticeResource(resource_utils.Resource, object):
    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class Solstice(importer.Importer, object):
    def __init__(self):
        super(Solstice, self).__init__(module_name='solstice')

    def get_module_path(self):
        """
        Returns path where tpNameIt module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpDccLib
                    mod_dir = tpDccLib.__path__[0]
                except Exception:
                    return None

        return mod_dir


def init(do_reload=False, import_libs=True):
    """
    Initializes module
    :param do_reload: bool, Whether to reload modules or not
    """

    if import_libs:
        import tpPyUtils
        tpPyUtils.init(do_reload=do_reload)
        import tpDccLib
        tpDccLib.init(do_reload=do_reload)
        import tpQtLib
        tpQtLib.init(do_reload=do_reload)
        import tpNameIt
        tpNameIt.init(do_reload=do_reload)
        import artellapipe
        artellapipe.init(do_reload=do_reload)

    from solstice.core import project

    solstice_importer = importer.init_importer(importer_class=Solstice, do_reload=do_reload)

    global logger
    global resource
    logger = solstice_importer.logger
    resource = SolsticeResource

    solstice_importer.import_modules()
    solstice_importer.import_packages(
        only_packages=True,
        order=['solstice.launcher', 'solstice.core', 'solstice.core.tagnode'],
        skip_modules=['solstice.pipeline.userSetup']
    )
    if do_reload:
        solstice_importer.reload_all()

    naming_file = path_utils.clean_path(os.path.join(os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename), 'naming.json'))

    artella.set_project(project.Solstice, resource, naming_file)


def get_project_path():
    """
    Returns path where default Artella project is located
    :return: str
    """

    return path_utils.clean_path(os.path.dirname(__file__))


def get_project_config_path():
    """
    Returns path where default Solstice project config is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(get_project_path(), artella_defines.ARTELLA_PROJECT_CONFIG_FILE_NAME))


def get_project_changelog_path():
    """
    Returns path where default Artella project changelog is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(get_project_path(), artella_defines.ARTELLA_PROJECT_CHANGELOG_FILE_NAME))


def get_project_shelf_path():
    """
    Returns path where Solstice project shelf file is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(get_project_path(), artella_defines.ARTELLA_PROJECT_SHELF_FILE_NAME))


def get_project_menu_path():
    """
    Returns path where Solstice project menu file is located
    :return: str
    """

    return path_utils.clean_path(os.path.join(get_project_path(), artella_defines.ARTELLA_PROJECT_SHELF_FILE_NAME))
