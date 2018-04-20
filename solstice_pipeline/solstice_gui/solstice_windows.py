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

    @classmethod
    def run(cls):
        if cls.docked:
            return dock_window(cls)
        else:
            win = cls()
            win.show()
            win.raise_()
            return win
