#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pipelinizer.py
# by Tomas Poveda
# Base wrapper classes for Solstice windows
# ______________________________________________________________________
# ==================================================================="""

import uuid

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from solstice_utils import solstice_maya_utils
from resources import solstice_resource


class Dialog(QDialog, object):
    """
    Class to create basic Maya docked windows
    """

    name = 'Solstice Tools'
    title = 'Solstice Tools'
    version = '1.0'
    dock = False

    def __init__(self, **kwargs):
        super(Dialog, self).__init__(parent=solstice_maya_utils.get_maya_window())

        # Window needs to have a unique name to avoid problems with Maya workspaces
        self.callbacks = list()

        self.setWindowTitle(kwargs.get('title', self.title))
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setFocusPolicy(Qt.StrongFocus)
        self.main_layout = None

        self.custom_ui()

    def add_callback(self, callback_id):
        self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(callback_id=callback_id))

    def remove_callbacks(self):
        for c in self.callbacks:
            try:
                self.callbacks.remove(c)
                del c
            except Exception as e:
                pass
        self.callbacks = []

    def custom_ui(self):
        if self.main_layout is None:
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            self.setLayout(self.main_layout)

            title_layout = QHBoxLayout()
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(0)
            title_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.main_layout.addLayout(title_layout)

            self.logo_view = QGraphicsView()
            self.logo_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.logo_view.setMaximumHeight(100)
            self._logo_scene = QGraphicsScene()
            self._logo_scene.setSceneRect(QRectF(0, 0, 2000, 100))
            self.logo_view.setScene(self._logo_scene)
            self.logo_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.logo_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.logo_view.setFocusPolicy(Qt.NoFocus)

            title_background_pixmap = solstice_resource.pixmap(name='solstice_pipeline', extension='png')
            self._logo_scene.addPixmap(title_background_pixmap)
            title_layout.addWidget(self.logo_view)

    def set_logo(self, logo_file_name, extension='png', offset=(930, 0)):
        solstice_logo_pixmap = solstice_resource.pixmap(name=logo_file_name, extension=extension)
        solstice_logo = self._logo_scene.addPixmap(solstice_logo_pixmap)
        solstice_logo.setOffset(offset[0], offset[1])

    def resizeEvent(self, event):
        # TODO: Take the width from the QGraphicsView not hardcoded :)
        self.logo_view.centerOn(1000, 0)
        return super(Dialog, self).resizeEvent(event)

    def cleanup(self):
        self.remove_callbacks()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def __del__(self):
        self.cleanup()
