#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_task.py
# by Tomas Poveda
# Module that contains base class for creating sanity check tasks
# ______________________________________________________________________
# ==================================================================="""

import traceback
import threading

from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_splitters
from solstice_pipeline.solstice_checks import solstice_validator
from solstice_checks import solstice_checkgroups


class TexturesValidator(solstice_validator.SanityCheckValidator, object):
    def __init__(self, asset):
        super(TexturesValidator, self).__init__(title='Textures Validator')

        self._asset = asset

        self._check = solstice_checkgroups.TexturesSanityCheck(asset=self._asset, auto_fix=True, stop_on_error=True)
        self._check.check_btn.setVisible(False)
        self.scroll_layout.addWidget(self._check)

        self.splitter = solstice_splitters.SplitterLayout()
        self.ok_btn = QPushButton('Continue')
        self.main_layout.addLayout(self.splitter)
        self.main_layout.addWidget(self.ok_btn)

        self.ok_btn.setVisible(False)
        self.ok_btn.clicked.connect(self._on_ok)

        self._check.checkDone.connect(self.update_log_text)
        self._check.checkFinished.connect(self.check_finished)

    def _update_progress_bar(self):
        super(TexturesValidator, self)._update_progress_bar()
        if self._event.is_set():
            self._timer.stop()
            self._progress_bar.setVisible(False)
            self.ok_btn.setVisible(True)

    def _on_ok(self):
        self.close()

    def check(self):
        if not self._asset:
            self.close()
            return False
        super(TexturesValidator, self).check()
        self._event = threading.Event()
        try:
            threading.Thread(target=self.do_check, args=(self._event,), name='SolsticeTexturesValidator').start()
        except Exception as e:
            sp.logger.debug(str(e))
            sp.logger.debug(traceback.format_exc())
            return False
        self.exec_()

    def do_check(self, event):
        self._check._on_do_check()
        event.set()
