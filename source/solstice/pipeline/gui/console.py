#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Console widget that can be used as basic output log
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys
from io import StringIO

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *


class SolsticeConsole(QTextEdit, object):
    def __init__(self, parent=None):
        super(SolsticeConsole, self).__init__(parent=parent)

        self._buffer = StringIO()
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setStyleSheet(
            """
            QTextEdit { background-color : rgba(0, 0, 0, 180); color : white; }
            """
        )

        self.customContextMenuRequested.connect(self._generate_context_menu)

    def __getattr__(self, attr):
        """
        Fall back to the buffer object if an attribute cannot be found
        """

        return getattr(self._buffer, attr)

    def write(self, msg):
        """
        Add message to the console's output, on a new line
        :param msg: str
        """

        self.insertPlainText(msg + '\n')
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        sys.solstice.logger.debug('{}\n'.format(msg))

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
        sys.solstice.logger.error('{}\n'.format(msg))

    def write_ok(self, msg):
        """
        Adds an ok green message to the console
        :param msg: str
        """

        msg_html = "<font color=\"Lime\">: " + msg + "\n</font><br>"
        self.insertHtml(msg_html)
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        sys.solstice.logger.debug('{}\n'.format(msg))

    def write_warning(self, msg):
        """
        Adds a warning yellow message to the console
        :param msg: str
        """

        msg_html = "<font color=\"Yellow\">: " + msg + "\n</font><br>"
        self.insertHtml(msg_html)
        self.moveCursor(QTextCursor.End)
        self._buffer.write(unicode(msg))
        sys.solstice.logger.warning('{}\n'.format(msg))

    def clear(self):
        self.setText('')

    def output_buffer_to_file(self, filepath):
        pass

    def _generate_context_menu(self, pos):
        """
        Internal function that generates context menu of the console
        :param pos: QPos
        :return: QMneu
        """

        menu = self.createStandardContextMenu()
        clear_action = QAction('Clear', menu)
        clear_action.triggered.connect(self.clear)
        menu.addSeparator()
        menu.addAction(clear_action)
        menu.popup(self.mapToGlobal(pos))


