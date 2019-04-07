#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_windows.py
# by Tomas Poveda
# Base wrapper classes for Solstice windows
# ______________________________________________________________________
# ==================================================================="""

import webbrowser

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_config
from solstice_pipeline.solstice_gui import solstice_dragger, solstice_animations
from solstice_pipeline.resources import solstice_resource

if sp.is_maya():
    try:
        from shiboken import wrapInstance
    except ImportError:
        from shiboken2 import wrapInstance
    from solstice_pipeline.solstice_utils import solstice_maya_utils
elif sp.is_houdini():
    from solstice_pipeline.solstice_utils import solstice_houdini_utils


class WindowStatusBar(QStatusBar, object):
    def __init__(self, parent=None):
        super(WindowStatusBar, self).__init__(parent)

        self._info_url = None

        self.setSizeGripEnabled(True)
        self.setStyleSheet("""
                QStatusBar
                {
                    border-bottom-left-radius: 5;
                    border-bottom-right-radius: 5;
                    background-color: rgb(50,50,50);
                }
                QSizeGrip
                {
                    image:url(:/icons/size_grip);
                    width:16px;
                    height:16px;
                }
                """)

        self._info_btn = QPushButton()
        self._info_btn.setIconSize(QSize(25, 25))
        self._info_btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._info_btn.setIcon(solstice_resource.icon('info1'))
        self._info_btn.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self.addWidget(self._info_btn)
        self.showMessage(' ')

        self._info_btn.clicked.connect(self._on_open_url)

    def showMessage(self, text):
        if self.has_url():
            text = '          {}'.format(text)
        super(WindowStatusBar, self).showMessage(text)

    def set_info_url(self, url):
        self._info_url = url

    def has_url(self):
        if self._info_url:
            return True

        return False

    def show_info(self):
        self._info_btn.setVisible(True)

    def hide_info(self):
        self._info_btn.setVisible(False)

    def _on_open_url(self):
        if self._info_url:
            webbrowser.open_new_tab(self._info_url)


class Window(QMainWindow, object):
    """
    Class to create basic Maya docked windows
    """

    name = 'SolsticeDockedWindow'
    title = 'Solstice Tools'
    version = '1.0'

    def __init__(self, parent=None):

        if parent is None:
            if sp.is_maya():
                parent = solstice_maya_utils.get_maya_window()
            elif sp.is_houdini():
                parent = solstice_houdini_utils.get_houdini_window()

        super(Window, self).__init__(parent=parent)

        self.setParent(parent)

        self.callbacks = list()
        self.settings = solstice_config.create_config(self.__class__.name)

        self.setObjectName(self.name)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setWindowTitle('{} - {}'.format(self.title, self.version))
        self.main_layout = None

        self.setStatusBar(WindowStatusBar())

        self.custom_ui()

        if not self.statusBar().has_url():
            self.statusBar().hide_info()

        for widget in self.parent().findChildren(QMainWindow):
            if widget is not self:
                if widget.objectName() == self.objectName():
                    widget.close()

    def set_info_url(self, url):
        if not url:
            return

        self.statusBar().set_info_url(url)

    def add_callback(self, callback_id):
        if sp.is_maya():
            self.callbacks.append(solstice_maya_utils.MCallbackIdWrapper(callback_id=callback_id))

    def remove_callbacks(self):
        for c in self.callbacks:
            try:
                self.callbacks.remove(c)
                del c
            except Exception as e:
                sp.logger.error('Impossible to clean callback {}'.format(c))
                sp.logger.error(str(e))
        self.callbacks = list()

    def custom_ui(self):

        base_widget = QWidget()
        base_widget.setAutoFillBackground(False)
        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        base_widget.setLayout(base_layout)
        self.setCentralWidget(base_widget)

        self.main_title = solstice_dragger.WindowDragger(parent=self)
        base_layout.addWidget(self.main_title)

        self.main_widget = QFrame()
        self.main_widget.setObjectName('mainFrame')
        self.main_widget.setFrameShape(QFrame.NoFrame)
        self.main_widget.setFrameShadow(QFrame.Plain)
        self.main_widget.setStyleSheet("""
        QFrame#mainFrame
        {
        background-color: rgb(35, 35, 35);
        border-radius: 5px;
        }""")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)
        base_layout.addWidget(self.main_widget)

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

    def fade_close(self):
        solstice_animations.fade_window(start=1, end=0, duration=400, object=self, on_finished=self.close)

    def cleanup(self):
        self.remove_callbacks()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    # def deleteLater(self):
    #     self.cleanup()
    #     super(Window, self).deleteLater()


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