#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pipelinizer.py
# by Tomas Poveda
# Base wrapper classes for Solstice windows
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

try:
    from shiboken import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance

import solstice_pipeline as sp
from solstice_utils import solstice_maya_utils, solstice_config
from resources import solstice_resource


class WindowDragger(QFrame, object):
    """
    Class to create custom window dragger for Solstice Tools
    """

    def __init__(self, parent=None, on_close=None):
        super(WindowDragger, self).__init__()

        self._parent = parent
        self._mouse_press_pos = None
        self._mouse_move_pos = None
        self._dragging_threshold = 5
        self._on_close = on_close

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(35, 35, 35))
        self.setPalette(palette)
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setAutoFillBackground(True)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 0, 15, 0)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(solstice_resource.pixmap('solstice_tools', category='icons').scaled(20, 20, Qt.KeepAspectRatio))
        title_text = QLabel(parent.windowTitle())

        main_layout.addWidget(lbl_icon)
        main_layout.addWidget(title_text)
        main_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        main_layout.addWidget(buttons_widget)

        buttons_widget.setLayout(buttons_layout)
        button_minimized = QPushButton()
        button_minimized.setIconSize(QSize(25, 25))
        button_minimized.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        button_minimized.setIcon(solstice_resource.icon('minimize'))
        button_minimized.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_maximized = QPushButton()
        self._button_maximized.setIcon(solstice_resource.icon('maximize'))
        self._button_maximized.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._button_maximized.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_maximized.setIconSize(QSize(25, 25))
        self._button_restored = QPushButton()
        self._button_restored.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._button_restored.setVisible(False)
        self._button_restored.setIcon(solstice_resource.icon('restore'))
        self._button_restored.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_restored.setIconSize(QSize(25, 25))
        button_closed = QPushButton()
        button_closed.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        button_closed.setIcon(solstice_resource.icon('close'))
        button_closed.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        button_closed.setIconSize(QSize(25, 25))

        buttons_layout.addWidget(button_minimized)
        buttons_layout.addWidget(self._button_maximized)
        buttons_layout.addWidget(self._button_restored)
        buttons_layout.addWidget(button_closed)

        self._button_maximized.clicked.connect(self._on_maximize_window)
        button_minimized.clicked.connect(self._on_minimize_window)
        self._button_restored.clicked.connect(self._on_restore_window)
        button_closed.clicked.connect(self._on_close_window)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_press_pos = event.globalPos()
            self._mouse_move_pos = event.globalPos() - self._parent.pos()
        super(WindowDragger, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            global_pos = event.globalPos()
            if self._mouse_press_pos:
                moved = global_pos - self._mouse_press_pos
                if moved.manhattanLength() > self._dragging_threshold:
                    diff = global_pos - self._mouse_move_pos
                    self._parent.move(diff)
                    self._mouse_move_pos = global_pos - self._parent.pos()
        super(WindowDragger, self).mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._button_maximized.isVisible():
            self._on_maximize_window()
        else:
            self._on_restore_window()

    def mouseReleaseEvent(self, event):
        if self._mouse_press_pos is not None:
            if event.button() == Qt.LeftButton:
                moved = event.globalPos() - self._mouse_press_pos
                if moved.manhattanLength() > self._dragging_threshold:
                    event.ignore()
                self._mouse_press_pos = None
        super(WindowDragger, self).mouseReleaseEvent(event)

    def _on_maximize_window(self):
        self._button_restored.setVisible(True)
        self._button_maximized.setVisible(False)
        self._parent.setWindowState(Qt.WindowMaximized)

    def _on_minimize_window(self):
        self._parent.setWindowState(Qt.WindowMinimized)

    def _on_restore_window(self):
        self._button_restored.setVisible(False)
        self._button_maximized.setVisible(True)
        self._parent.setWindowState(Qt.WindowNoState)

    def _on_close_window(self):
        self._parent.close()


class Window(QMainWindow, object):
    """
    Class to create basic Maya docked windows
    """

    name = 'SolsticeDockedWindow'
    title = 'Solstice Tools'
    version = '1.0'

    def __init__(self, parent=solstice_maya_utils.get_maya_window()):
        super(Window, self).__init__(parent=parent)

        self.setParent(parent)

        self.callbacks = list()
        self.settings = solstice_config.create_config(self.__class__.name)

        self.setObjectName(self.name)
        self.setWindowFlags(self.windowFlags() ^ Qt.FramelessWindowHint)
        self.setWindowTitle('{} - {}'.format(self.title, self.version))
        self.main_layout = None

        self.statusBar().setSizeGripEnabled(True)

        self.custom_ui()

        for widget in self.parent().findChildren(QMainWindow):
            if widget is not self:
                if widget.objectName() == self.objectName():
                    widget.close()

    def add_callback(self, callback_id):
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

        base_widget = QFrame()
        base_widget.setFrameShape(QFrame.StyledPanel)
        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        base_widget.setLayout(base_layout)
        self.setCentralWidget(base_widget)

        main_title = WindowDragger(parent=self)
        base_layout.addWidget(main_title)

        self.main_widget = QWidget()
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

    def cleanup(self):
        self.remove_callbacks()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def deleteLater(self):
        self.cleanup()
        super(Window, self).deleteLater()


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