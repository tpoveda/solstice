#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that shows the changelog for the current version of Solstice Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json
from collections import OrderedDict

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import dialog, accordion


class SolsticeChangelog(dialog.Dialog, object):

    name = 'SolsticeChangelog'
    title = 'Solstice Tools - Changelog'
    version = '1.1'

    def __init__(self):
        super(SolsticeChangelog, self).__init__()

    def custom_ui(self):
        super(SolsticeChangelog, self).custom_ui()
        self.set_logo('solstice_changelog_logo')

        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.resize(550, 600)

        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignTop)
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)
        ok_btn = QPushButton('OK')
        ok_btn.setMinimumHeight(30)
        ok_btn.setStyleSheet("""
        border-bottom-left-radius: 5;
        border-bottom-right-radius: 5;
        background-color: rgb(50, 50, 50);
        """)
        ok_btn.clicked.connect(self.fade_close)
        self.main_layout.addWidget(scroll)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(ok_btn)
        scroll.setWidget(central_widget)
        central_widget.setLayout(scroll_layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.main_layout = scroll_layout

        # ===========================================================================================

        self.version_accordion = accordion.AccordionWidget(parent=self)
        self.version_accordion.rollout_style = accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.version_accordion)

        # ===========================================================================================

        changelog_json_file = sp.get_solstice_changelog_file()
        if not os.path.isfile(changelog_json_file):
            return

        with open(changelog_json_file, 'r') as f:
            changelog_data = json.load(f, object_pairs_hook=OrderedDict)
        if not changelog_data:
            return

        changelog_versions = [float(key) for key in changelog_data.keys()]
        for version in reversed(sorted(changelog_versions)):
            self._create_version(str(version), changelog_data[str(version)])

        last_version_item = self.version_accordion.item_at(0)
        last_version_item.set_collapsed(False)

    def _create_version(self, version, elements):

        version_widget = QWidget()
        version_layout = QVBoxLayout()
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setSpacing(0)
        version_layout.setAlignment(Qt.AlignTop)
        version_widget.setLayout(version_layout)
        self.version_accordion.add_item(version, version_widget, collapsed=True)

        version_label = QLabel()
        version_layout.addWidget(version_label)
        version_text = ''
        for item in elements:
            version_text += '- {}\n'.format(item)
        version_label.setText(version_text)

        self.main_layout.addSpacing(5)


def run():
    solstice_changelog = SolsticeChangelog()
    solstice_changelog.exec_()
