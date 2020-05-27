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
import logging.config

# =================================================================================

PACKAGE = 'solstice'

# =================================================================================


def init(import_libs=True, dev=False):
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
    import artellapipe.loader
    from solstice import register

    logger = create_logger()
    register.register_class('logger', logger)

    if import_libs:
        import artellapipe.loader
        artellapipe.loader.init(import_libs=True, dev=dev)

    from solstice.core import project

    modules_to_skip = ['solstice.bootstrap']
    importer.init_importer(package=PACKAGE, skip_modules=modules_to_skip)

    artellapipe.loader.set_project(project.Solstice)


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
