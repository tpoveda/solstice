#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_validator.py
# by Tomas Poveda
# Module that contains base class to create validator dialogs
# ______________________________________________________________________
# ==================================================================="""

import threading
import traceback

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_dialog, solstice_splitters
from solstice_checks import solstice_checkgroups


class SanityCheckValidator(solstice_dialog.Dialog, object):

    checkFinished = Signal()

    def __init__(self, name='Validator', title='Validator', auto_accept=True):
        self.name = name
        self._title = title
        super(SanityCheckValidator, self).__init__()

        self._valid_check = False
        self._auto_accept = True

    def check(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress_bar)
        self._timer.start(200)

        self._event = threading.Event()
        try:
            threading.Thread(target=self.do_check, args=(self._event,), name=self.name).start()
        except Exception as e:
            sp.logger.debug(str(e))
            sp.logger.debug(traceback.format_exc())
            return False
        self.exec_()

    def do_check(self, event):
        event.set()

    def get_logo(self):
        return 'solstice_validator_logo'

    def custom_ui(self):
        super(SanityCheckValidator, self).custom_ui()
        self.set_logo(self.get_logo())

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self._event = threading.Event()

        self.title = solstice_splitters.Splitter(self._title.upper())
        self.main_layout.addWidget(self.title)

        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_widget.setLayout(self.scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll_widget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.main_layout.addWidget(scroll)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximum(50)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("QProgressBar {border: 0px solid grey; border-radius:4px; padding:0px} QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1, stop: 0 rgb(245, 180, 148), stop: 1 rgb(75, 70, 170)); }")
        self.main_layout.addWidget(self._progress_bar)

        self._progress_text = QLabel('Validating ...')
        self._progress_text.setAlignment(Qt.AlignCenter)
        self._progress_text.setStyleSheet("QLabel { background-color : rgba(0, 0, 0, 180); color : white; }")
        font = self._progress_text.font()
        font.setPointSize(10)
        self._progress_text.setFont(font)
        self.main_layout.addWidget(self._progress_text)

        self._log_text = QTextEdit()
        self._log_text.setVisible(False)
        self._log_text.setReadOnly(True)
        self.main_layout.addWidget(self._log_text)

        self.splitter = solstice_splitters.SplitterLayout()
        self.ok_btn = QPushButton('Continue')
        self.main_layout.addLayout(self.splitter)
        self.main_layout.addWidget(self.ok_btn)

        self.ok_btn.setVisible(False)
        self.ok_btn.clicked.connect(self._on_ok)

    def add_error_to_log(self, task_name, message):
        message = '[{0}] - {1}\n'.format(task_name, message)
        self._log_text.setText(self._log_text.toPlainText() + message)

    def update_log_text(self, task, valid):
        if not valid:
            self.add_error_to_log(task.get_name(), task.get_error_message())

    def is_valid(self):
        return self._valid_check

    def check_finished(self, valid):

        self._valid_check = valid

        if valid:
            self._progress_text.setText('VALIDATION CHECK WAS SUCCESSFUL!')
            self._progress_text.setStyleSheet('background-color: rgb(45, 90, 45);')
            if self._auto_accept:
                self._on_ok()
        else:
            # self._progress_text.setVisible(False)
            self._progress_text.setText('VALIDATION CHECK FAILED!')
            self._progress_text.setStyleSheet('background-color: rgb(45, 90, 45);')
            self._log_text.setVisible(True)

    def _on_ok(self):
        self.close()

    def _on_repaint(self):
        self.repaint()

    def _update_progress_bar(self):
        if self._progress_bar.value() >= self._progress_bar.maximum():
            self._progress_bar.setValue(0)
        self._progress_bar.setValue(self._progress_bar.value() + 1)

        # This is called when the validation has finished
        if self._event.is_set():
            self._timer.stop()
            self._progress_bar.setVisible(False)
            self.ok_btn.setVisible(True)

    def closeEvent(self, event):
        self.checkFinished.emit()
        self._timer.stop()
        return super(SanityCheckValidator, self).closeEvent(event)

# =================================================================================================================


class TexturesValidator(SanityCheckValidator, object):
    def __init__(self, asset):
        super(TexturesValidator, self).__init__(title='Textures Validator')

        self._asset = asset

        self._check = solstice_checkgroups.TexturesSanityCheck(asset=self._asset, auto_fix=True, stop_on_error=True)
        self._check.check_btn.setVisible(False)
        self.scroll_layout.addWidget(self._check)

        self._check.checkDone.connect(self.update_log_text)
        self._check.checkFinished.connect(self.check_finished)

    def get_logo(self):
        return 'solstice_texturesvalidator_logo'

    def do_check(self, event):
        self._check._on_do_check()
        super(TexturesValidator, self).do_check(event)


class ShadingValidator(SanityCheckValidator, object):
    def __init__(self, asset):
        super(ShadingValidator, self).__init__(
            name='SolsticeShadingValidator',
            title='Shading Validator'
        )

        self._asset = asset

        self._check = solstice_checkgroups.AssetPublishSantiyCheck(asset=self._asset, file_type='shading', auto_fix=True, stop_on_error=True)
        self._check.check_btn.setVisible(False)
        self.scroll_layout.addWidget(self._check)

        self._check.checkDone.connect(self.update_log_text)
        self._check.checkFinished.connect(self.check_finished)
        self._check.checkBeingFixed.connect(self._on_repaint)

    def get_logo(self):
        return 'solstice_shadingvalidator_logo'

    def check(self):
        if not self._asset:
            self.close()
            return False
        super(ShadingValidator, self).check()

    def do_check(self, event):
        self._check._on_do_check()
        super(ShadingValidator, self).do_check(event)
