#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella loader implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import os
import inspect
import logging.config


def init(do_reload=False, import_libs=True, dev=False):
    """
    Initializes Solstice library
    """

    # Without default_integrations=False, PyInstaller fails during launcher generation
    if not dev:
        import sentry_sdk
        try:
            sentry_sdk.init("https://c75c06d8349449a1a829c04732ba3e5c@sentry.io/1761556")
        except (RuntimeError, ImportError):
            sentry_sdk.init("https://c75c06d8349449a1a829c04732ba3e5c@sentry.io/1761556", default_integrations=False)

    from tpDcc.libs.python import importer
    from solstice import register

    logger = create_logger()
    register.register_class('logger', logger)

    class SolsticeCore(importer.Importer, object):
        def __init__(self, debug=False):
            super(SolsticeCore, self).__init__(module_name='solstice', debug=debug)

        def get_module_path(self):
            """
            Returns path where solstice module is stored
            :return: str
            """

            try:
                mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
            except Exception:
                try:
                    mod_dir = os.path.dirname(__file__)
                except Exception:
                    try:
                        import solstice
                        mod_dir = solstice.__path__[0]
                    except Exception:
                        return None

            return mod_dir

    packages_order = [
        'solstice.core'
    ]

    if import_libs:
        import artellapipe.loader
        artellapipe.loader.init(do_reload=do_reload, import_libs=True, dev=dev)

    from solstice.core import project

    solstice_core_importer = importer.init_importer(importer_class=SolsticeCore, do_reload=False, debug=dev)
    solstice_core_importer.import_packages(
        only_packages=False,
        order=packages_order,
        skip_modules=['solstice.bootstrap']
    )
    if do_reload:
        solstice_core_importer.reload_all()

    import artellapipe.loader
    artellapipe.loader.set_project(project.Solstice, do_reload=do_reload)


def create_logger():
    """
    Returns logger of current module
    """

    logging.config.fileConfig(get_logging_config(), disable_existing_loggers=False)
    logger = logging.getLogger('solstice')

    return logger


def create_logger_directory():
    """
    Creates artellapipe logger directory
    """

    artellapipe_logger_dir = os.path.normpath(os.path.join(os.path.expanduser('~'), 'solstice', 'logs'))
    if not os.path.isdir(artellapipe_logger_dir):
        os.makedirs(artellapipe_logger_dir)


def get_logging_config():
    """
    Returns logging configuration file path
    :return: str
    """

    create_logger_directory()

    return os.path.normpath(os.path.join(os.path.dirname(__file__), '__logging__.ini'))


def get_logging_level():
    """
    Returns logging level to use
    :return: str
    """

    if os.environ.get('SOLSTICE_LOG_LEVEL', None):
        return os.environ.get('SOLSTICE_LOG_LEVEL')

    return os.environ.get('SOLSTICE_LOG_LEVEL', 'WARNING')
