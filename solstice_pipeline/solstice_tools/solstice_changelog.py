#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_changelog.py
# by Tomas Poveda
# Tool that shows the changelog for the current version of Solstice Tools
# ______________________________________________________________________
# ==================================================================="""

import os
import json
from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *

from solstice_gui import solstice_dialog, solstice_group, solstice_splitters


class SolsticeChangelog(solstice_dialog.Dialog, object):

    name = 'Changelog'
    title = 'Solstice Tools - Changelog'
    version = '1.0'
    docked = False

    def __init__(self, name='ChangelogWindow', parent=None, **kwargs):
        super(SolsticeChangelog, self).__init__(name=name, parent=parent)

    def custom_ui(self):
        super(SolsticeChangelog, self).custom_ui()
        self.set_logo('solstice_changelog_logo')
        self.setFixedWidth(600)
        self.setMaximumHeight(800)

        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(2, 2, 2, 2)
        scroll_layout.setSpacing(2)
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)
        self.main_layout.addWidget(scroll)
        scroll.setWidget(central_widget)
        central_widget.setLayout(scroll_layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.main_layout = scroll_layout

        # ===========================================================================================

        changelog_json_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'changelog.json')
        if not os.path.isfile(changelog_json_file):
            return

        changelog_data = None
        with open(changelog_json_file, 'r') as f:
            changelog_data = json.load(f, object_pairs_hook=OrderedDict)
        if not changelog_data:
            return

        changelog_data = OrderedDict(sorted(changelog_data.items(), reverse=True))

        for version, elements in changelog_data.items():
            self._create_version(version, elements)

    def _create_version(self, version, elements):
        version_group = solstice_group.SolsticeGroup(title='Version {}'.format(version))
        version_group.set_collapsable(False)
        version_group.main_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addWidget(version_group)

        for item in elements:
            item_lbl = QLabel('- {}'.format(item))
            version_group.main_layout.addWidget(item_lbl)

        self.main_layout.addSpacing(5)





def run():
    solstice_changelog = SolsticeChangelog()
    solstice_changelog.exec_()