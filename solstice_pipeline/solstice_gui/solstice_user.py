#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_user.py
# by Tomas Poveda
# Module that cantains a widget to show user images
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import getpass

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_worker
from solstice_pipeline.solstice_utils import solstice_python_utils as python
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella
from solstice_pipeline.solstice_gui import solstice_spinner
from resources import solstice_resource


class UserWidget(solstice_spinner.WaitSpinner, object):
    def __init__(self, parent=None):
        super(UserWidget, self).__init__(parent=parent)

        self._user_pixmap = solstice_resource.pixmap(name='no_user', extension='png')

        self.setStyleSheet("QWidget{background: transparent;}")

        self.user_lbl = QLabel()
        self.frame_layout.addWidget(self.user_lbl)
        self.user_lbl.setVisible(True)

        self.login()

    def destroy(self):
        if self._worker:
            self._worker.stop()

    def login(self):
        self._worker = solstice_worker.Worker(app=QApplication.instance())
        self._worker.workCompleted.connect(self._on_worker_completed)
        self._worker.workFailure.connect(self._on_worker_failure)
        self._worker.start()

        self._worker_uid = self._worker.queue_work(self._download_user, {})

        sp.logger.debug('Getting user info ...')

    def _download_user(self, data):
        # Make sure that user_login.json file is sync
        user_login_file = os.path.normpath(
            os.path.join(sp.get_solstice_project_path(), 'Assets', 'Scripts', 'PIPELINE', '__working__','user_login.json'))
        if not os.path.isfile(user_login_file):
            artella.synchronize_file(user_login_file)
        if not user_login_file:
            sp.logger.debug('Error during logging into Artella, please try it later!')
            return False

        user_name = '{0}_{1}'.format(getpass.getuser(), sys.platform)
        user_id = None
        data = python.load_json(user_login_file)
        if user_name not in data['users'.title()]:
            artella.lock_asset(user_login_file)
            try:
                file_status = artella.get_status(user_login_file)
                file_info = file_status.references.values()[0]
                user_id = file_info.locked_by_display
                sp.logger.debug('ID: {}'.format(user_id))
                if not user_id:
                    sp.logger.debug('Error during logging into Artella, please try it later!')
                    return False
                data['users'.title()][user_name] = user_id
                python.write_json(user_login_file, data)
                artella.upload_new_asset_version(user_login_file, 'Added user: {}'.format(user_name))
                artella.unlock_asset(user_login_file)
            except Exception as e:
                sp.logger.error(str(e))
                artella.unlock_asset(user_login_file)
                return False
        else:
            user_id = data['users'.title()][user_name]

        user_image = artella.get_user_avatar(user_id=user_id)
        image = QImage()
        self._timer.stop()
        self._timer.timeout.disconnect()
        try:
            image.loadFromData(user_image.read())
            self.user_lbl.setPixmap(QPixmap(image).scaled(QSize(80, 80), Qt.KeepAspectRatio))
            self.user_lbl.setVisible(True)
            self.thumbnail_label.setVisible(False)

        except Exception as e:
            sp.logger.debug(str(e))
            self.user_lbl.setPixmap(self._user_pixmap)
            self.user_lbl.setVisible(True)
            self.thumbnail_label.setVisible(False)

    def _on_worker_completed(self):
        print('Worker completed')

    def _on_worker_failure(self, uid, msg):
        self._timer.stop()
        sp.logger.error('Worker {0} : {1}'.format(uid, msg))



