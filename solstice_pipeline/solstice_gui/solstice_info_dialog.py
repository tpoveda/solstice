#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_info_dialog.py
# by Tomas Poveda
# Dialog used to synchronize info between Artella and Maya
# ______________________________________________________________________
# ==================================================================="""

import threading

import solstice_pipeline as sp
from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

from solstice_gui import solstice_animations
from resources import solstice_resource

if sp.dcc == sp.SolsticeDCC.Maya:
    import maya.cmds as cmds
    from solstice_utils import solstice_maya_utils


class InfoDialog(QDialog, object):
    def __init__(self):

        if sp.dcc == sp.SolsticeDCC.Maya:
            parent = solstice_maya_utils.get_maya_window()
        else:
            parent = None

        super(InfoDialog, self).__init__(parent=parent)

        name = 'SolsticeInfoDialog'

        if sp.dcc == sp.SolsticeDCC.Maya:
            if cmds.window(name, exists=True):
                cmds.deleteUI(name, window=True)
            elif cmds.windowPref(name, exists=True):
                cmds.windowPref(name, remove=True)

        self.setObjectName(name)
        self.setWindowTitle('Solstice Tools - Info Dialog')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setFixedSize(QSize(280, 180))

        self.setStyleSheet(
            """
            background:transparent;
            background-color: rgb(30, 30, 30);
            """
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        logo = solstice_resource.pixmap(name='solstice_logo', extension='png')
        logo_layout = QHBoxLayout()
        logo_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        logo_lbl = QLabel()
        logo_lbl.setPixmap(logo)
        logo_layout.addWidget(logo_lbl)
        logo_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        main_layout.addLayout(logo_layout)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximum(100)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }");

        main_layout.addWidget(self._progress_bar)

        self._progress_text = QLabel('Synchronizing Artella Files ... Please wait!')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        main_layout.addWidget(self._progress_text)

        self._timer = None

    def do(self, text, name, fn, args=None, show=True):

        if not fn:
            return

        if show:
            self.show()

        self._progress_text.setText(text)

        self._event = threading.Event()
        if not args:
            args = (self._event,)
        else:
            args.append(self._event)
            args = tuple(args)

        if self._timer:
            self._timer.stop()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress_bar)
        self._timer.start(200)

        thread = threading.Thread(target=fn, args=args, name=name).start()

        return thread, self._event

    def set_text(self, text):
        self._progress_text.setText(text)

    def show(self):
        super(InfoDialog, self).show()
        solstice_animations.fade_window(start=0, end=1, duration=2000, object=self)
        solstice_animations.slide_window(start=30, end=0, duration=1500, object=self)

    def hide_dialog(self):
        self._stop_timer()
        self.hide()
        # solstice_animations.fade_window(start=1, end=0, duration=2000, object=self, on_finished=self._stop_timer)
        # solstice_animations.slide_window(start=0, end=30, duration=1000, object=self)

    def closeEvent(self, event):
        self._stop_timer()
        event.accept()
        # return super(InfoDialog, self).closeEvent(event)

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                sp.logger.debug('Process stopped by user!')
                self._event.set()
                self._update_progress_bar()

    def _update_progress_bar(self):
        if self._progress_bar.value() >= self._progress_bar.maximum():
            self._progress_bar.setValue(0)
        self._progress_bar.setValue(self._progress_bar.value() + 1)
        if self._event.is_set():
            self.hide_dialog()

    def _stop_timer(self):
        if self._timer:
            self._timer.stop()


