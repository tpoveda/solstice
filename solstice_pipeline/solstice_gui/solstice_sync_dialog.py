#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sync_dialog.py
# by Tomas Poveda
# Dialog used to synchronize info between Artella and Maya
# ______________________________________________________________________
# ==================================================================="""

import os
import threading
import traceback

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_utils import solstice_maya_utils
from solstice_utils import solstice_artella_utils as artella

from resources import solstice_resource


class SolsticeSyncSplash(QSplashScreen, object):
    def __init__(self, *args, **kwargs):
        super(SolsticeSyncSplash, self).__init__(*args, **kwargs)

        self.mousePressEvent = self.MousePressEvent
        self._canceled = False

    def MousePressEvent(self, event):
        pass


class SolsticeSync(QDialog, object):
    sync_finished = Signal()

    def __init__(self):
        super(SolsticeSync, self).__init__()
        self.setParent(solstice_maya_utils.get_maya_window())
        self.custom_ui()

    def custom_ui(self):

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        splash_pixmap = solstice_resource.pixmap('solstice_sync_splash')
        splash = SolsticeSyncSplash(splash_pixmap)
        self._splash_layout = QVBoxLayout()
        self._splash_layout.setAlignment(Qt.AlignBottom)
        splash.setLayout(self._splash_layout)
        self.main_layout.addWidget(splash)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximum(50)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }")
        self._splash_layout.addWidget(self._progress_bar)

        self._progress_text = QLabel('Synchronizing Artella Files ... Please wait!')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        self._splash_layout.addWidget(self._progress_text)

        self.setFixedSize(splash_pixmap.size())

    def sync(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress_bar)
        self._timer.start(200)

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Escape:
            super(SolsticeSync, self).keyPressEvent(event)

    def sync_files(self, event):
        pass

    def _update_progress_bar(self):

        if self._progress_bar.value() >= self._progress_bar.maximum():
            self._progress_bar.setValue(0)
        self._progress_bar.setValue(self._progress_bar.value() + 1)

    def closeEvent(self, event):
        self.sync_finished.emit()
        self._timer.stop()
        return super(SolsticeSync, self).closeEvent(event)


class SolsticeSyncFile(SolsticeSync, object):
    def __init__(self, files=None):
        super(SolsticeSyncFile, self).__init__()
        self._files = files

    def _update_progress_bar(self):
        super(SolsticeSyncFile, self)._update_progress_bar()

        if self._event.is_set():
            self._timer.stop()
            self.close()

    def sync(self):
        if not self._files:
            self.close()
        super(SolsticeSyncFile, self).sync()
        self._event = threading.Event()
        try:
            threading.Thread(target=self.sync_files, args=(self._event,), name='SolsticeSyncFilesThread').start()
        except Exception as e:
            sp.logger.debug(str(e))
            sp.logger.debug(traceback.format_exc())
        self.exec_()

    def sync_files(self, event):
        for p in self._files:
            file_path = os.path.relpath(p, sp.get_solstice_assets_path())
            self._progress_text.setText('Syncing file: {0} ... Please wait!'.format(file_path))
            artella.synchronize_file(p)
            sp.register_asset(p)
        event.set()


class SolsticeSyncPath(SolsticeSync, object):
    def __init__(self, paths=None):
        super(SolsticeSyncPath, self).__init__()
        self._paths = paths

    def _update_progress_bar(self):
        super(SolsticeSyncPath, self)._update_progress_bar()

        if self._event.is_set():
            self._timer.stop()
            self.close()

    def sync(self):
        if not self._paths:
            self.close()
        super(SolsticeSyncPath, self).sync()
        self._event = threading.Event()
        try:
            threading.Thread(target=self.sync_files, args=(self._event,), name='SolsticeSyncPathsThread').start()
        except Exception as e:
            sp.logger.debug(str(e))
            sp.logger.debug(traceback.format_exc())
        self.exec_()

    def sync_files(self, event):
        for p in self._paths:
            file_path = os.path.relpath(p, sp.get_solstice_assets_path())
            self._progress_text.setText('Syncing files of folder: {0} ... Please wait!'.format(file_path))
            artella.synchronize_path(p)
            sp.register_asset(p)
        event.set()


class SolsticeSyncGetDeps(SolsticeSync, object):
    def __init__(self):
        super(SolsticeSyncGetDeps, self).__init__()

    def custom_ui(self):
        super(SolsticeSyncGetDeps, self).custom_ui()

        self._splash_layout.addItem(QSpacerItem(0, 5))

        cancel_btn_layout = QHBoxLayout()
        cancel_btn_layout.setContentsMargins(0, 0, 0, 0)
        cancel_btn_layout.setSpacing(0)
        self._splash_layout.addLayout(cancel_btn_layout)
        cancel_btn_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self._cancel_btn = QPushButton('Cancel')
        self._cancel_btn.setVisible(False)
        self._cancel_btn.setMaximumWidth(100)
        cancel_btn_layout.addWidget(self._cancel_btn)
        cancel_btn_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self._cancel_btn.clicked.connect(self._cancel_sync)

    def _update_progress_bar(self):
        super(SolsticeSyncPath, self)._update_progress_bar()

        if self._canceled:
            self._event.set()

        if self._event.is_set():
            self._timer.stop()
            self.close()

    def _cancel_sync(self):
        self._canceled = True
