#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pipelinizer.py
# by Tomas Poveda
# Base wrapper classes for Solstice windows
# ______________________________________________________________________
# ==================================================================="""

import inspect

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from solstice_utils import solstice_maya_utils, solstice_config
from resources import solstice_resource


class Window(MayaQWidgetDockableMixin, QWidget):
    """
    Class to create basic Maya docked windows
    """

    name = 'SolsticeDockedWindow'
    title = 'Solstice Tools'
    version = '1.0'
    dock = False

    def __init__(self, parent=solstice_maya_utils.get_maya_window(), **kwargs):
        super(Window, self).__init__(parent=parent)

        self.callbacks = list()
        self.settings = solstice_config.create_config(self.__class__.name)

        self.setObjectName(self.__class__.name)
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
            # self.main_widget = QWidget()
            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            # self.main_widget.setLayout(self.main_layout)
            # self.setCentralWidget(self.main_widget)
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
        return super(Window, self).resizeEvent(event)

    def cleanup(self):
        self.remove_callbacks()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def __del__(self):
        self.cleanup()

    @classmethod
    def window_closed(cls):
        parent = solstice_maya_utils.get_maya_window()
        children = parent.findChildren(QWidget)
        instance = None
        instance_workspace = None
        for child in children:
            if cls.name in child.objectName():
                if not child.objectName().endswith('WorkspaceControl'):
                    instance = child
                    break
                elif child.objectName().endswith('WorkspaceControl'):
                    instance_workspace = child
        if instance:
            instance.cleanup()
        if instance_workspace:
            if cmds.workspaceControl(instance_workspace.objectName(), exists=True):
                cmds.deleteUI(instance_workspace.objectName())

    @classmethod
    def run(cls):
        parent = solstice_maya_utils.get_maya_window()
        children = parent.findChildren(QWidget)
        instance = None
        for child in children:
            if cls.name in child.objectName():
                if not child.objectName().endswith('WorkspaceControl'):
                    instance = child
                    break
        if instance is not None:
            instance.window().close()

        cls.window_closed()

        instance = cls()
        instance.setProperty('saveWindowPref', True)

        close_command = """from solstice_qt.QtWidgets import *; 
        from solstice_pipeline.solstice_utils import solstice_maya_utils;
        parent=solstice_maya_utils.get_maya_window();
        instance=parent.findChild(QWidget, "{}");
        if instance:
            instance.cleanup();
            instance.parent().setParent(None);
            instance.parent().deleteLater();""".format(cls.name)
        close_command = inspect.cleandoc(close_command)

        if cmds.workspaceControl(instance.objectName() + 'WorkspaceControl', exists=True):
            cmds.deleteUI(instance.objectName() + 'WorkspaceControl')

        instance.show(dockable=True, save=True, closeCallback=close_command)
        instance.window().raise_()
        instance.raise_()
        instance.isActiveWindow()

        return instance


class DockWindow(QMainWindow, object):
    def __init__(self, name='SolsticeWindow', title='SolsticeWindow', parent=None, use_scroll=False):
        super(DockWindow, self).__init__(parent)

        self.setObjectName(name)
        self.setWindowTitle(title)

        self.main_layout = QVBoxLayout()
        main_widget = QWidget()

        self.docks = list()
        self.connect_tab_change = True
        self.tab_change_hide_show = True

        if use_scroll:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(main_widget)
            self._scroll_widget = scroll

            main_widget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
            self.setCentralWidget(scroll)
        else:
            self.setCentralWidget(main_widget)

        main_widget.setLayout(self.main_layout)
        self.main_widget = main_widget
        self.main_layout.expandingDirections()
        self.main_layout.setContentsMargins(1,1,1,1)
        self.main_layout.setSpacing(2)

        self.custom_ui()

    def keyPressEvent(self, event):
        return

    def custom_ui(self):
        self.centralWidget().hide()
        self.setTabPosition(Qt.TopDockWidgetArea, QTabWidget.East)
        self.setDockOptions(self.AnimatedDocks | self.AllowTabbedDocks)

    def _get_tab_bar(self):
        children = self.children()
        for child in children:
            if isinstance(child, QTabBar):
                return child

    def _get_dock_widgets(self):
        children = self.children()
        found = list()
        for child in children:
            if isinstance(child, QDockWidget):
                found.append(child)
        return found

    def _tab_changed(self, index):
        if not self.tab_change_hide_show:
            return
        docks = self._get_dock_widgets()
        docks[index].hide()
        docks[index].show()

    def add_dock(self, widget, name):
        docks = self._get_dock_widgets()
        for dock in docks:
            if dock.windowTitle() == name:
                dock.deleteLater()
                dock.close()
        dock_widget = QDockWidget(name, self)
        dock_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        dock_widget.setAllowedAreas(Qt.TopDockWidgetArea)
        dock_widget.setWidget(widget)
        self.addDockWidget(Qt.TopDockWidgetArea, dock_widget)
        if docks:
            self.tabifyDockWidget(docks[-1], dock_widget)
        dock_widget.show()
        dock_widget.raise_()
        tab_bar = self._get_tab_bar()
        if tab_bar:
            if self.connect_tab_change:
                tab_bar.currentChanged.connect(self._tab_changed)
                self.connect_tab_change = False
            tab_bar.setCurrentIndex(0)
        return dock_widget