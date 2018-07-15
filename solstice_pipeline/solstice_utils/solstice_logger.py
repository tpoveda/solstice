#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_logger.py
# by Tomas Poveda
# Module that contains solstice logger functionality
# ______________________________________________________________________
# ==================================================================="""

import os
import logging
import json

import solstice_pipeline


class LoggerLevel:
    def __init__(self):
        pass

    INFO = logging.INFO
    WARNING = logging.WARNING
    DEBUG = logging.DEBUG


class Logger(object):
    def __init__(self, name, level=LoggerLevel.INFO):
        self._name  = name
        self._level = level
        self._logger = None
        self._initialized = False
        self.create()

    def create(self):
        """
        Creates new solstice logger
        """

        format_ = '[%(asctime)s - %(levelname)s:]: %(name)s - %(message)s'

        try:
            logging_settings_file = None
            logging_file_name = 'logging.json'
            for root, dirs, files in os.walk(solstice_pipeline.__path__[0]):
                for f in files:
                    if f == logging_file_name:
                        logging_settings_file = os.path.join(root, f)
                        break

            if logging_settings_file and os.path.isfile(logging_settings_file):
                with open(os.path.join(os.path.dirname(__file__), logging_settings_file), str("rt")) as f:
                    config = json.load(f)
                logging.config.dictConfig(config)
            else:
                logging.basicConfig(format=format_) if format_ else logging.basicConfig()
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)
            hdlr = logging.FileHandler(self.get_log_file(),  mode='w')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            self._logger.addHandler(hdlr)
        except Exception:
            logging.basicConfig(format=format_) if format_ else logging.basicConfig()
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)
            hdlr = logging.FileHandler(self.get_log_file(), mode='w')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            self._logger.addHandler(hdlr)

    def enable(self):
        """
        Enables debugging on the logger
        """

        self._level = logging.DEBUG
        self._logger.setLevel(self._level)

    def disable(self):
        """
        Disables debugging on the logger
        """

        self._level = logging.INFO
        self._logger.setLevel(self._level)

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
    # endregion

    # region Private Functions
    def get_log_file(self):
        """
        Returns solstice log file
        :return: str
        """

        return os.path.join(solstice_pipeline.__path__[0], self._name + '.log')
    # endregion
