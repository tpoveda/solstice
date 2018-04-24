#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pipelinizer.py
# by Tomas Poveda
# Base wrapper classes for Solstice windows
# ______________________________________________________________________
# ==================================================================="""

import weakref

from Qt.QtCore import *
from Qt.QtWidgets import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_utils import solstice_qt_utils, solstice_maya_utils
from resources import solstice_resource


def dock_window(window_class):
    cmds.evalDeferred(lambda *args: solstice_qt_utils.dock_solstice_widget(widget_class=window_class))


def delete_instances(window_class):
    for ins in window_class.instances:
        sp.logger.debug('Deleting {} window'.format(ins))
        try:
            ins.setParent(None)
            ins.deleteLater()
        except:
            # Ignore the deletion exception if the actual parent has already been deleted by Maya
            pass
        window_class.instances.remove(ins)
        del ins


class Window(QMainWindow, object):
    """
    Class to create basic Maya docked windows
    """

    title = 'Solstice Tools'
    version = '1.0'
    docked = False

    instances = list()

    def __init__(self, name='SolsticeDockedWindow', parent=None, layout=None, **kwargs):
        super(Window, self).__init__(parent=parent)

        delete_instances(self.__class__)
        self.__class__.instances.append(weakref.proxy(self))

        if not self.docked:
            if parent is None:
                self.setParent(solstice_maya_utils.get_maya_window())

            self.setObjectName(name)
            self.setWindowTitle(kwargs.get('title', self.title))
            self.setWindowFlags(self.windowFlags() | Qt.Window)
            self.setFocusPolicy(Qt.StrongFocus)
            self.main_layout = None
        else:
            self.main_layout = layout

        self.custom_ui()

    def custom_ui(self):
        if self.main_layout is None:
            self.main_widget = QWidget()
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            self.main_widget.setLayout(self.main_layout)
            self.setCentralWidget(self.main_widget)

            title_layout = QHBoxLayout()
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
        return super(Window, self).resizeEvent(event)

    @classmethod
    def run(cls):
        if cls.docked:
            return dock_window(cls)
        else:
            win = cls()
            win.show()
            win.raise_()
            return win
