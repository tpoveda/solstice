#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains a widget to show Artella user info
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import getpass

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice.pipeline as sp
from solstice.pipeline.gui import spinner
from solstice.pipeline.utils import worker, pythonutils as python, artellautils as artella
from solstice.pipeline.resources import resource


class UserInfoWidget(QWidget, object):

    updatedAvailability = Signal(bool)

    def __init__(self, parent=None):
        self._user_pixmap = resource.pixmap(name='no_user', category='images', extension='png')
        self._user_name = getpass.getuser()
        if sys.platform == 'win32':
            self._os_icon = resource.pixmap(name='windows', category='icons', extension='png')
        else:
            self._os_icon = resource.pixmap(name='apple', category='icons', extension='png')

        super(UserInfoWidget, self).__init__(parent=parent)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self._worker = worker.Worker(app=QApplication.instance())
        self._worker.workCompleted.connect(self._on_worker_completed)
        self._worker.workFailure.connect(self._on_worker_failure)
        self._worker.start()

        self._artella_color = QColor(255, 255, 0, 255)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_artella_avilability)
        self.start_check()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def destroy(self):
        if self._timer:
            self._timer.stop()

    def start_check(self):
        if not self._timer.isActive():
            self._timer.start(5000)

    def hideEvent(self, event):
        self._timer.stop()
        super(UserInfoWidget, self).hideEvent(event)

    def closeEvent(self, event):
        self._timer.stop()
        super(UserInfoWidget, self).closeEvent(event)

    def set_pixmap(self, user_pixmap):
        self._user_pixmap = user_pixmap

    def paintEvent(self, event):
        super(UserInfoWidget, self).paintEvent(event)

        painter = QPainter(self)
        fixed_image = QImage(128, 128, QImage.Format_ARGB32_Premultiplied)
        fixed_image.fill(0)
        image_painter = QPainter(fixed_image)
        clip = QPainterPath()
        clip.addEllipse(32, 32, 90, 90)
        image_painter.setClipPath(clip)
        image_painter.drawPixmap(0, 0, 128, 128, self._user_pixmap)
        image_painter.end()
        painter.drawPixmap(50, -15, 80, 80, QPixmap.fromImage(fixed_image))
        painter.drawText(80, 80, self._user_name)
        painter.drawPixmap(105, 68, 15, 15, self._os_icon)
        painter.setBrush(self._artella_color)
        painter.setPen(self._artella_color)
        painter.drawEllipse(122, 72, 6, 6)
        painter.end()

    def _check_artella_avilability(self):
        self._worker_uid = self._worker.queue_work(self._artella_is_available, {})

    def _artella_is_available(self, data):
        available = sp.artella_is_available()
        if available:
            self.enable_artella()
        else:
            self.disable_artella()
        self.updatedAvailability.emit(available)

    def _on_worker_completed(self, uid, data):
        sys.solstice.logger.debug('Worker completed')

    def _on_worker_failure(self, uid, msg):
        self._timer.stop()
        sys.solstice.logger.error('Worker {0} : {1}'.format(uid, msg))

    def enable_artella(self):
        self._artella_color = QColor(0, 255, 0, 255)
        self.repaint()

    def disable_artella(self):
        self._artella_color = QColor(255, 0, 0, 255)
        self.repaint()


class UserWidget(QWidget, object):
    def __init__(self, parent=None):
        super(UserWidget, self).__init__(parent=parent)

        self._user_pixmap = resource.pixmap(name='no_user', category='icons', extension='png')
        self.setStyleSheet("QWidget{background: transparent;}")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.stack_widget = QStackedWidget()
        main_layout.addWidget(self.stack_widget)

        self.wait_widget = spinner.WaitSpinner(spinner_type=spinner.SpinnerType.Circle)
        self.user_info = UserInfoWidget()
        self.stack_widget.addWidget(self.wait_widget)
        self.stack_widget.addWidget(self.user_info)

        self.get_user()

    def destroy(self):
        if self._worker:
            self._worker.stop()
        if self.user_info:
            self.user_info.destroy()

    def get_user(self):
        self.stack_widget.setCurrentIndex(0)
        self._worker = worker.Worker(app=QApplication.instance())
        self._worker.workCompleted.connect(self._on_worker_completed)
        self._worker.workFailure.connect(self._on_worker_failure)
        self._worker.start()
        self._worker_uid = self._worker.queue_work(self._download_user, {})

    def _download_user(self, data):

        try:
            # Make sure that user_login.json file is sync
            user_login_file = os.path.normpath(os.path.join(sp.get_solstice_project_path(), 'Assets', 'Scripts', 'PIPELINE', '__working__', 'user_login.json'))
            if not os.path.isfile(user_login_file):
                artella.synchronize_file(user_login_file)
            if not user_login_file:
                sys.solstice.logger.debug('Error during logging into Artella, please try it later!')
                return False

            # We force the unlock of the file
            try:
                artella.unlock_file(user_login_file)
            except Exception as e:
                pass

            user_name = '{0}_{1}'.format(getpass.getuser(), sys.platform)
            user_pixmap = resource.pixmap(name='no_user', category='images', extension='png')
            data = python.load_json(user_login_file)
            if user_name not in data['users'.title()]:
                valid_lock = artella.lock_file(user_login_file, force=True)
                if not valid_lock:
                    sys.solstice.logger.debug('Impossible to get user avatar. Applying default one ...')
                    self._update_user_info(pixmap=user_pixmap)
                    return
                try:
                    file_status = artella.get_status(user_login_file)
                    file_info = file_status.references.values()[0]
                    user_id = file_info.locked_by_display
                    sys.solstice.logger.debug('ID: {}'.format(user_id))
                    if not user_id:
                        sys.solstice.logger.debug('Error during logging into Artella, please try it later!')
                        self._update_user_info(pixmap=user_pixmap)
                        return
                    data['users'.title()][user_name] = user_id
                    python.write_json(user_login_file, data)
                    artella.upload_new_asset_version(user_login_file, 'Added user: {}'.format(user_name))
                    artella.unlock_file(user_login_file)
                except Exception as e:
                    sys.solstice.logger.error(str(e))
                    artella.unlock_file(user_login_file)
                    self._update_user_info(pixmap=user_pixmap)
                    return
            else:
                user_id = data['users'.title()][user_name]

            user_image = artella.get_user_avatar(user_id=user_id)
            image = QImage()
            try:
                image.loadFromData(user_image.read())
                user_pixmap = QPixmap(image)
            except Exception as e:
                user_pixmap = self._user_pixmap
                sys.solstice.logger.debug(str(e))
        except Exception:
            user_pixmap = resource.pixmap(name='no_user', category='images', extension='png')

        self._update_user_info(pixmap=user_pixmap)
        try:
            artella.unlock_file(user_login_file)
        except Exception as e:
            pass

    def _update_user_info(self, pixmap):
        self.user_info.set_pixmap(pixmap)
        self.stack_widget.setCurrentIndex(1)

    def _on_worker_completed(self):
        sys.solstice.logger.debug('Worker completed')

    def _on_worker_failure(self, uid, msg):
        sys.solstice.logger.error('Worker {0} : {1}'.format(uid, msg))
