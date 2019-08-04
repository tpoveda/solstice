#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtCore import *
from Qt.QtWidgets import *


class BaseWidget(QWidget, object):
    def __init__(self, parent=None):
        super(BaseWidget, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        """
        Creates base layout for widget
        Extend in child classes
        """

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        self.setLayout(base_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)
        base_layout.addWidget(scroll_area)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        scroll_widget.setLayout(self.main_layout)

    def setup_signals(self):
        pass
