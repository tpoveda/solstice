#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_user.py
# by Tomas Poveda
# Module that cantains a widget to show user images
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from resources import solstice_resource


class UserWidget(QWidget, object):
    def __init__(self, name, role, user_pixmap=None, parent=None):
        super(UserWidget, self).__init__(parent=parent)

        self._name = name
        self._role = role
        if user_pixmap is None:
            user_pixmap = solstice_resource.pixmap(name='no_user', extension='png').scaled(QSize(80, 80))

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self._user_icon = QLabel()
        self._user_icon.setPixmap(user_pixmap)

        name_label = QLabel(self._name)
        name_label.setAlignment(Qt.AlignCenter)
        role_label = QLabel(self._role)
        role_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self._user_icon)
        main_layout.addWidget(role_label)


