#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widgets to drag PySide windows and dialogs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from solstice.pipeline.resources import resource


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

        self.setObjectName('titleFrame')
        self.setStyleSheet("""
        QFrame#titleFrame
        {
            background-color: rgb(35, 35, 35);
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        """)

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
        lbl_icon.setPixmap(resource.pixmap('solstice_tools', category='icons').scaled(20, 20, Qt.KeepAspectRatio))
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
        self._button_minimized = QPushButton()
        self._button_minimized.setIconSize(QSize(25, 25))
        self._button_minimized.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._button_minimized.setIcon(resource.icon('minimize'))
        self._button_minimized.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_maximized = QPushButton()
        self._button_maximized.setIcon(resource.icon('maximize'))
        self._button_maximized.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._button_maximized.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_maximized.setIconSize(QSize(25, 25))
        self._button_restored = QPushButton()
        self._button_restored.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self._button_restored.setVisible(False)
        self._button_restored.setIcon(resource.icon('restore'))
        self._button_restored.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        self._button_restored.setIconSize(QSize(25, 25))
        button_closed = QPushButton()
        button_closed.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        button_closed.setIcon(resource.icon('close'))
        button_closed.setStyleSheet('QWidget {background-color: rgba(255, 255, 255, 0); border:0px;}')
        button_closed.setIconSize(QSize(25, 25))

        buttons_layout.addWidget(self._button_minimized)
        buttons_layout.addWidget(self._button_maximized)
        buttons_layout.addWidget(self._button_restored)
        buttons_layout.addWidget(button_closed)

        self._button_maximized.clicked.connect(self._on_maximize_window)
        self._button_minimized.clicked.connect(self._on_minimize_window)
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
        self._parent.fade_close()


class DialogDragger(WindowDragger, object):
    def __init__(self, parent=None, on_close=None):
        super(DialogDragger, self).__init__(parent=parent, on_close=on_close)

        for btn in [self._button_maximized, self._button_minimized, self._button_restored]:
            btn.setEnabled(False)
            btn.setVisible(False)

    def mouseDoubleClickEvent(self, event):
        return
