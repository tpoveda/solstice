#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_login.py
# by Tomas Poveda
# Dialog used to login to Artella
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import getpass

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_worker
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella
from solstice_pipeline.solstice_utils import solstice_python_utils as python
from solstice_pipeline.solstice_gui import solstice_dialog, solstice_spinner
from solstice_pipeline.resources import solstice_resource

reload(artella)


class SolsticeUserPassword(QWidget, object):

    onLogin = Signal(str, str)

    def __init__(self, parent=None):
        super(SolsticeUserPassword, self).__init__(parent=parent)

        _user_pixmap = solstice_resource.pixmap('user', category='icons').scaled(QSize(24, 24))
        _password_pixmap = solstice_resource.pixmap('password', category='icons').scaled(QSize(24, 24))
        _login_icon = solstice_resource.icon('go')

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        user_icon = QLabel()
        user_icon.setPixmap(_user_pixmap)
        self.user_line = QLineEdit()
        self.user_line.setMinimumWidth(100)
        password_icon = QLabel()
        password_icon.setPixmap(_password_pixmap)
        self.password_line = QLineEdit()
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_line.setMinimumWidth(100)

        self.login_btn = QPushButton()
        self.login_btn.setIcon(_login_icon)

        main_layout.addWidget(user_icon)
        main_layout.addWidget(self.user_line)
        main_layout.addWidget(password_icon)
        main_layout.addWidget(self.password_line)
        main_layout.addWidget(self.login_btn)

        self.login_btn.clicked.connect(self._on_login)
        self.user_line.returnPressed.connect(self._on_login)
        self.password_line.returnPressed.connect(self._on_login)
        self.user_line.textChanged.connect(self._update_ui)
        self.password_line.textChanged.connect(self._update_ui)

        self._update_ui()

    def can_login(self):
        return self.user_line.text() != '' and self.password_line.text() != ''

    def _on_login(self):
        if not self.can_login():
            return

        user = self.user_line.text()
        password = self.password_line.text()
        self.onLogin.emit(user, password)

    def _update_ui(self):
        self.login_btn.setEnabled(self.can_login())


class SolsticeLoginProcess(solstice_spinner.WaitSpinner, object):
    def __init__(self, parent=None):
        super(SolsticeLoginProcess, self).__init__(parent=parent)

        self._worker = None
        self._worker_uid = None

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

    def login(self, user, password):

        self._worker = solstice_worker.Worker(app=QApplication.instance())
        self._worker.workCompleted.connect(self._on_worker_completed)
        self._worker.workFailure.connect(self._on_worker_failure)
        self._worker.start()

        self._worker_uid = self._worker.queue_work(self._login_user_password, {'user': user, 'password': password})

        print('Login with {0} | {1}'.format(user, password))

    def destroy(self):
        if self._worker:
            self._worker.stop()

    def _login_user_password(self, data):

        # First we check that the given user info is valid and we can connect to Artella
        user = data['user']
        password = data['password']
        can_connect = artella.login_to_artella(user=user, password=password)
        if not can_connect:
            sp.logger.error('Impossible to connect to Artella, check your user and password please·!')
            return False

        # Make sure that user_login.json file is sync
        user_login_file = os.path.normpath(os.path.join(sp.get_solstice_project_path(), 'Assets', 'Scripts', 'PIPELINE', '__working__', 'user_login.json'))
        if not os.path.isfile(user_login_file):
            artella.synchronize_file(user_login_file)
        if not user_login_file:
            sp.logger.debug('Error during logging into Artella, please try it later!')
            return False

        user_name = '{0}_{1}'.format(getpass.getuser(), sys.platform)
        user_id = None
        data = python.load_json(user_login_file)
        if user_name not in data['users'.title()]:
            artella.lock_file(user_login_file)
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
                artella.unlock_file(user_login_file)
            except Exception as e:
                sp.logger.error(str(e))
                artella.unlock_file(user_login_file)
                return False
        else:
            user_id = data['users'.title()][user_name]

    def _on_worker_completed(self):
        print('Worker completed')

    def _on_worker_failure(self, uid, msg):
        self._timer.stop()
        sp.logger.error('Worker {0} : {1}'.format(uid, msg))


class SolsticeLoggedWidget(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeLoggedWidget, self).__init__(parent=parent)



class SolsticeLoginWidget(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeLoginWidget, self).__init__(parent=parent)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        # main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        self.stack_widget = QStackedWidget()
        main_layout.addWidget(self.stack_widget)

        self.user_password = SolsticeUserPassword()
        self.login_process = SolsticeLoginProcess()
        self.logged = SolsticeLoggedWidget()

        self.stack_widget.addWidget(self.user_password)
        self.stack_widget.addWidget(self.login_process)
        self.stack_widget.addWidget(self.logged)

        self.user_password.onLogin.connect(self._login)

    def _login(self, user, password):
        if user is not None and password is not None and user != '' and password != '':
            self.stack_widget.setCurrentIndex(1)
            self.login_process.login(user=user, password=password)


class SolsticeLogin(solstice_dialog.Dialog, object):

    name = 'Solstice_Login'
    title = 'Solstice Tools - Solstice Login'
    version = '1.0'
    docked = False

    def __init__(self, name='SolsticeLoginWindow', parent=None, **kwargs):
        super(SolsticeLogin, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticeLogin, self).custom_ui()
        self.set_Logo('solstice_login_logo')

        self.setMaximumHeight(50)

        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

