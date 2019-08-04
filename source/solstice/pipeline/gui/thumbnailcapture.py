#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to capture thumbnails
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import shutil

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import modelpanel
from solstice.pipeline.utils import pythonutils, qtutils

if sp.is_maya():
    import maya.cmds as cmds

reload(modelpanel)

_instance = None


class ThumbnailCaptureDialog(QDialog, object):

    DEFAULT_WIDTH = 250
    DEFAULT_HEIGHT = 250

    capturing = Signal(str)
    captured = Signal(str)

    def __init__(self, path='', parent=None, start_frame=None, end_frame=None, step=1):
        parent = parent or sys.solstice.dcc.get_main_window()
        super(ThumbnailCaptureDialog, self).__init__(parent=parent)

        self.setObjectName('thumbnailCaptureDialog')
        self.setWindowTitle('Solstice Tools - Thumbnail Capturer')

        self._path = path
        self._step = step
        self._end_frame = None
        self._start_frame = None
        self._capture_path = None

        start_frame = start_frame or int(sys.solstice.dcc.get_current_frame())
        end_frame = end_frame or int(sys.solstice.dcc.get_current_frame())

        self.set_start_frame(start_frame)
        self.set_end_frame(end_frame)

        self._capture_btn = QPushButton('Capture')
        self._model_panel_widget = modelpanel.ModelPanelWidget(self)

        vbox = QVBoxLayout(self)
        vbox.setObjectName(self.objectName()+'Layout')
        vbox.addWidget(self._model_panel_widget)
        vbox.addWidget(self._capture_btn)
        self.setLayout(vbox)

        width = self.DEFAULT_WIDTH * 1.5
        height = (self.DEFAULT_HEIGHT * 1.5) + 50

        self.set_width_height(width, height)
        self.center_window()

        self._capture_btn.clicked.connect(self.capture)

    def path(self):
        """
        Reutns the destination path
        :return: str
        """

        return self._path

    def set_path(self, path):
        """
        Sets teh destination path
        :param path: str
        """

        self._path = path

    def end_frame(self):
        """
        Returns teh end frame of the playblast
        :return: int
        """

        return self._end_frame

    def set_end_frame(self, end_frame):
        """
        Sets the end frame of the playblast
        :param end_frame: int
        """

        self._end_frame = end_frame

    def start_frame(self):
        """
        Returns teh start frame of the playblast
        :return: int
        """

        return self._start_frame

    def set_start_frame(self, start_frame):
        """
        Sets the start frame of the playblast
        :param end_frame: int
        """

        self._start_frame = start_frame

    def step(self):
        """
        Returns the step amount of the playblast.
        If the step is set to 2, it will playblast every 2 seconds
        :return: int
        """

        return self._step

    def set_width_height(self, width ,height):
        """
        Sets the width and height of the window
        :param width: int
        :param height: int
        """

        x = self.geometry().x()
        y = self.geometry().y()
        self.setGeometry(x, y, width, height)

    def center_window(self):
        """
        Centers the widget to the center of the desktop
        """

        geometry = self.frameGeometry()
        pos = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(pos)
        center_point = QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())

    def capture_path(self):
        """
        Returns the location of the captured playblast
        :return: str
        """

        return self._capture_path

    def capture(self):
        """
        Captures a playblast and save it to the given path
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('Playblast capture is only supported in Maya!')
            return

        path = self.path()

        self.capturing.emit(path)
        model_panel = self._model_panel_widget.name()
        start_frame = self.start_frame()
        end_frame = self.end_frame()
        step = self.step()
        width = self.DEFAULT_WIDTH
        height = self.DEFAULT_HEIGHT
        self._capture_path = self._do_playblast(path, model_panel ,start_frame, end_frame, width, height, step=step)
        self.accept()
        self.captured.emit(self._capture_path)

        return self._capture_path

    def _do_playblast(self, filename, model_panel, start_frame, end_frame, width, height, step=1, playblast_renderer=None):
        """
        Wrapper for Maya playblast command
        :param filename: str
        :param model_panel: str
        :param start_frame: int
        :param end_frame: int
        :param width: int
        :param height: int
        :param step: list(int)
        :return: str
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('Playblast capture is only supported in Maya!')
            return

        sys.solstice.logger.debug('Playblasting {}'.format(filename))

        if start_frame == end_frame and os.path.exists(filename):
            os.remove(filename)

        frame = [i for i in range(start_frame, end_frame + 1, step)]

        model_panel = model_panel or sys.solstice.dcc.get_current_model_panel()
        if cmds.modelPanel(model_panel, query=True, exists=True):
            cmds.setFocus(model_panel)
            if playblast_renderer:
                cmds.modelEditor(model_panel, edit=True, rendererName=playblast_renderer)

        name, compression = os.path.splitext(filename)
        filename = filename.replace(compression, '')
        compression = compression.replace('.', '')
        off_screen = pythonutils.is_linux()

        path = cmds.playblast(
            format="image",
            viewer=False,
            percent=100,
            quality=100,
            frame=frame,
            width=width,
            height=height,
            filename=filename,
            endTime=end_frame,
            startTime=start_frame,
            offScreen=off_screen,
            forceOverwrite=True,
            showOrnaments=False,
            compression=compression,
        )

        if not path:
            raise Exception('Playblast was cancelled!')

        source = path.replace("####", str(int(0)).rjust(4, "0"))
        if start_frame == end_frame:
            target= source.replace(".0000.", ".")
            sys.solstice.logger.info("Renaming '%s' => '%s" % (source, target))
            os.rename(source, target)
            source = target

        sys.solstice.logger.info('Playblasted "{}"'.format(source))

        return source


def thumbnail_capture(path, start_frame=None, end_frame=None, step=1, clear_cache=False, captured=None, show=False, modifier=True):
    """
    Captres a playblast and save it to the given path
    :param path: str
    :param start_frame: int | None
    :param end_frame: int | None
    :param step: int
    :param clear_cache: bool
    :param captured: fn | None
    :param show: bool
    :param modifier: bool
    :return: ThumbnailCaptureDialog
    """

    global _instance

    def _clear_cache():
        dirname = os.path.dirname(path)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    if _instance:
        _instance.close()

    d = ThumbnailCaptureDialog(path=path, start_frame=start_frame, end_frame=end_frame, step=step)

    if captured:
        d.captured.connect(captured)

    if clear_cache:
        d.capturing.connect(_clear_cache)

    d.show()

    if not show and not (modifier and qtutils.is_control_modifier()):
        d.capture()
        d.close()

    _instance = d

    return _instance
