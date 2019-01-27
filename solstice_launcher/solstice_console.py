#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_launcher_utils.py
# by Tomas Poveda
# Solstice Console that can be used as basic output log during solstice
# launcher execution
# ______________________________________________________________________
# ==================================================================="""

from io import StringIO
import logging

from PySide.QtGui import *

import solstice_logger
import solstice_launcher_utils as utils


class SolsticeConsole(QTextEdit, object):
    def __init__(self, parent=None):
        super(SolsticeConsole, self).__init__(parent=parent)

        self._buffer = StringIO()
        self.setReadOnly(True)

        self.setStyleSheet(
            """
            QTextEdit { background-color : rgba(0, 0, 0, 180); color : white; }
            """
        )

        self.logger = solstice_logger.Logger(
            name='solstice_launcher',
            path=str(utils.get_system_config_directory(as_path=True)),
            level=solstice_logger.LoggerLevel.DEBUG)

    def write(self, msg):
        """
        Add message to the console's output, on a new line
        :param msg: str
        """

        self.insertPlainText(msg + '\n')
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        self.logger.debug('{}\n'.format(msg))

    def write_error(self, msg):
        """
        Adds an error message to the console
        :param msg: str
        """

        msg_html = "<font color=\"Red\">ERROR: " + msg + "\n</font><br>"
        msg = 'ERROR: ' + msg
        self.insertHtml(msg_html)
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        self.logger.debug('{}\n'.format(msg))

    def write_ok(self, msg):
        """
        Adds an ok green message to the console
        :param msg: str
        """

        msg_html = "<font color=\"Lime\">: " + msg + "\n</font><br>"
        self.insertHtml(msg_html)
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        self.logger.debug('{}\n'.format(msg))

    def set_info_level(self):
        """
        Sets console logging level to info
        """

        self.logger.setLevel(logging.INFO)

    def set_debug_level(self):
        """
        Sets console logging level to debug
        """

        self.logger.setLevel(logging.DEBUG)

    def __getattr__(self, attr):
        """
        Fall back to the buffer object if an attribute cannot be found
        """

        return getattr(self._buffer, attr)

    def output_buffer_to_file(self, filepath):
        pass