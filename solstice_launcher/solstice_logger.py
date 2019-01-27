#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_logger.py
# by Tomas Poveda
# Basic logger for Solstice Launcher
# ______________________________________________________________________
# ==================================================================="""

import os
import logging
import traceback
import logging.handlers

# ==================================================================================
LOGGERS = dict()
# ==================================================================================


class LoggerLevel:
    def __init__(self):
        pass

    INFO = logging.INFO
    WARNING = logging.WARNING
    DEBUG = logging.DEBUG


class Logger(object):
    def __init__(self, name, path, level=LoggerLevel.INFO):

        self._name = name
        self._level = level
        self._logger = None
        self._initialized = False
        self.create(path=path)

    # region Properties
    def get_level(self):
        return self._level

    def set_level(self, level):
        self._level = level

    level = property(get_level, set_level)
    # endregion

    # region Public Functions
    def create(self, path):

        # format_ = "%(levelname)s:%(name)s [%(filename)s:%(lineno)d]# %(message)s"
        format_ = '[%(asctime)s - %(levelname)s:]: %(name)s - %(message)s'

        try:
            logging_settings_file = self.get_log_file(path=path)
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)
            fh = logging.FileHandler(logging_settings_file)
            fh.setLevel(self._level)
            self._logger.addHandler(fh)
            rh = logging.handlers.RotatingFileHandler(logging_settings_file, 'w', backupCount=1)
            rh.setLevel(self._level)
            rh.setFormatter(format_)
            rh.doRollover()
            self._logger.addHandler(rh)
        except Exception as e:
            print('Impossible to create logger ... {}'.format(traceback.format_exc()))
            logging.basicConfig(format=format_) if format_ else logging.basicConfig()
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)

    def enable(self):
        """
        Enables debugging on the logger
        """

        self._level = logging.DEBUG
        self._logger.setLevel(self._level)
        self._initialized = True

    def disable(self):
        """
        Disables debugging on the logger
        """

        self._level = logging.INFO
        self._logger.setLevel(self._level)
        self._initialized = False

    def get_effective_level(self):
        return self._logger.getEffectiveLevel()

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        self._logger.log(lvl, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

    def get_log_file(self, path):
        """
        Returns the user log file
        :return: str
        """

        return os.path.join(path, '{}.log'.format(self._name))
    # endregion
