#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_errortracker.py
# by Tomas Poveda
# Tool to capture current Solstice Tools errors and trace calls
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import json
import time
import getpass
import tempfile
import datetime
import  urllib2
import webbrowser

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_dialog, solstice_splitters, solstice_sync_dialog
from solstice_pipeline.solstice_utils import solstice_python_utils, solstice_qt_utils, solstice_image
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella
from solstice_pipeline.resources import solstice_resource


class BugTracker(solstice_dialog.Dialog, object):

    name = 'Solstice_BugTracker'
    title = 'Solstice Tools - Bug Tracker'
    version = '1.0'
    docked = False

    def __init__(self, name='BugTrackerDialog', parent=None, **kwargs):
        super(BugTracker, self).__init__(name=name, parent=parent, **kwargs)

        self.screen_pixmap = None

    def custom_ui(self):
        super(BugTracker, self).custom_ui()

        self.set_logo('solstice_bugtracker_logo')

        _warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))

        self.capture_lbl = QLabel()
        self.capture_lbl.setAlignment(Qt.AlignCenter)
        self.trace_text = QTextEdit()
        self.trace_text.setReadOnly(True)
        self.send_btn = QPushButton('Send Bug')
        self.send_btn.setEnabled(False)

        note_layout = QHBoxLayout()
        note_layout.setAlignment(Qt.AlignLeft)
        note_icon = QLabel()
        note_icon.setPixmap(_warning_pixmap)
        note_text = QLabel('Error image will be uploaded to Artella server and all Solstice Team Members will be able to access to it.\nSo make sure your screen does not have sensible or confidential information')
        note_layout.addWidget(note_icon)
        note_layout.addWidget(solstice_qt_utils.get_horizontal_separator())
        note_layout.addWidget(note_text)

        self.main_layout.addWidget(self.capture_lbl)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addWidget(self.trace_text)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addLayout(note_layout)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())
        self.main_layout.addWidget(self.send_btn)

        self.send_btn.clicked.connect(self._on_send_bug)

    def update_ui(self):
        self.send_btn.setEnabled(self.screen_pixmap is not None and self.trace_text.toPlainText() != '')

    @staticmethod
    def get_bugs_folder():
        return os.path.normpath(os.path.join(sp.get_solstice_project_path(), 'Assets', 'Scripts', 'PIPELINE', '__working__', 'Bugs'))

    def update_capture(self):
        self.screen_pixmap = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        self.capture_lbl.setPixmap(self.screen_pixmap.scaled(850, 338, Qt.KeepAspectRatio))
        self.update_ui()

    def set_trace(self, trace):
        self.trace_text.setPlainText(str(trace))
        self.update_ui()

    def _on_send_bug(self):
        if self.screen_pixmap is None:
            return

        bugs_path = self.get_bugs_folder()
        solstice_sync_dialog.SolsticeSyncFile(files=[bugs_path]).sync()
        if not os.path.exists(bugs_path):
            sp.logger.error('Impossible to sync Solstice Bugs Folder ...')
            return

        user = '{0}_{1}'.format(getpass.getuser(), sys.platform)
        bug_name = os.path.join(bugs_path, 'bug_{}.bug'.format(user))
        bug_path = solstice_python_utils.add_unique_postfix(bug_name)

        temp_path = os.path.join(tempfile.mkdtemp(), 'solstice_error.png')
        self.screen_pixmap.save(temp_path)
        image_base64 = solstice_image.image_to_base64(image_path=temp_path)

        current_time = str(datetime.datetime.now())
        error_info = dict()
        error_info['user'] = user
        error_info['time'] = current_time
        error_info['bug'] = image_base64
        error_info['trace'] = self.trace_text.toPlainText()

        with open(bug_path, 'w') as f:
            json.dump(error_info, f)

        artella.upload_file(bug_path, comment='{0} | {1}'.format(current_time, user))

        msg = self.trace_text.toPlainText()
        msg += '\n----------------------------\n'
        msg += 'Bug Name: {}\n'.format(os.path.basename(bug_path))
        msg += 'Date: {}\n'.format(current_time)
        webbrowser.open("mailto:%s?subject=%s" % ('tpoveda@cgart3d.com', urllib2.quote(str(msg))))

        self.close()


def run(traceback):
    solstice_qt_utils.show_error(None, 'Critical error', 'Something went wrong while sync. Opening Bug Tracker ...!')
    time.sleep(1)
    bug = BugTracker()
    bug.update_capture()
    bug.set_trace(traceback)
    bug.exec_()
