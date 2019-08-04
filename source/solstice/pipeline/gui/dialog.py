#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base wrapper classes for Solstice dialogs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import dragger, animations
from solstice.pipeline.utils import qtutils
from solstice.pipeline.resources import resource

if sp.is_maya():
    from solstice.pipeline.utils import mayautils
elif sp.is_houdini():
    from solstice.pipeline.utils import houdiniutils


class Dialog(QDialog, object):
    """
    Class to create basic Maya docked windows
    """

    name = 'Solstice Tools'
    title = 'Solstice Tools'
    version = '1.0'

    def __init__(self, parent=None):

        if parent is None:
            parent = sys.solstice.dcc.get_main_window()

        super(Dialog, self).__init__(parent=parent)

        # Window needs to have a unique name to avoid problems with Maya workspaces
        self.callbacks = list()

        self.setObjectName(self.name)
        self.setWindowTitle('{0} - {1}'.format(self.title, self.version))
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        self.setFocusPolicy(Qt.StrongFocus)
        self.main_layout = None

        self.custom_ui()

        qtutils.center_widget_on_screen(self)

    def add_callback(self, callback_id):
        if sp.is_maya():
            self.callbacks.append(mayautils.MCallbackIdWrapper(callback_id=callback_id))

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

            dialog_layout = QVBoxLayout()
            dialog_layout.setContentsMargins(0, 0, 0, 0)
            dialog_layout.setSpacing(0)
            self.setLayout(dialog_layout)

            base_widget = QWidget()
            base_widget.setAutoFillBackground(False)
            base_layout = QVBoxLayout()
            base_layout.setContentsMargins(0, 0, 0, 0)
            base_layout.setSpacing(0)
            base_widget.setLayout(base_layout)
            dialog_layout.addWidget(base_widget)

            self.main_title = dragger.DialogDragger(parent=self)
            base_layout.addWidget(self.main_title)

            self.options_widget = QFrame()
            self.options_widget.setObjectName('mainFrame')
            self.options_widget.setFrameShape(QFrame.NoFrame)
            self.options_widget.setFrameShadow(QFrame.Plain)
            self.options_widget.setStyleSheet("""
            QFrame#mainFrame
            {
            background-color: rgb(35, 35, 35);
            border-radius: 5px;
            }""")
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            self.options_widget.setLayout(self.main_layout)
            base_layout.addWidget(self.options_widget)

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

            title_background_pixmap = resource.pixmap(name='solstice_pipeline', extension='png')
            self._logo_scene.addPixmap(title_background_pixmap)
            title_layout.addWidget(self.logo_view)

    def set_logo(self, logo_file_name, extension='png', offset=(930, 0)):
        solstice_logo_pixmap = resource.pixmap(name=logo_file_name, extension=extension)
        solstice_logo = self._logo_scene.addPixmap(solstice_logo_pixmap)
        solstice_logo.setOffset(offset[0], offset[1])

    def resizeEvent(self, event):
        # TODO: Take the width from the QGraphicsView not hardcoded :)
        self.logo_view.centerOn(1000, 0)
        return super(Dialog, self).resizeEvent(event)

    def fade_close(self):
        animations.fade_window(start=1, end=0, duration=400, object=self, on_finished=self.close)

    def cleanup(self):
        self.remove_callbacks()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def deleteLater(self):
        self.cleanup()
        super(Dialog, self).deleteLater()

    # def __del__(self):
    #     self.cleanup()
