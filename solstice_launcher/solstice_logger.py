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
import json

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
            logging_file_name = os.path.basename(logging_settings_file)
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f == logging_file_name:
                        logging_settings_file = os.path.join(root, f)
                        break

            if logging_settings_file and os.path.isfile(logging_settings_file):
                with open(os.path.join(os.path.dirname(__file__), logging_settings_file), str("rt")) as f:
                    config = json.load(f)
                logging.config.dictConfig(config)
            else:
                pass
                # logging.basicConfig(format=format_, filename=logging_settings_file) if format_ else logging.basicConfig()
                # logging.basicConfig(format=format_, filename=logging_settings_file)
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)
            fh = logging.FileHandler(logging_settings_file)
            fh.setLevel(self._level)
            self._logger.addHandler(fh)
        except Exception:
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
