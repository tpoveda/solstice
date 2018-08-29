#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_traymessage.py
# by Tomas Poveda
# Module that contains custom tray balloon widget
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.resources import solstice_resource


class SolsticeTrayMessage(QWidget, object):

    def __init__(self, parent=None):
        super(SolsticeTrayMessage, self).__init__(parent=parent)

        _solstice_icon = solstice_resource.icon('solstice')
        _artella_icon = solstice_resource.icon('artella')
        self._solstice_tools_icon = solstice_resource.icon('solstice_tools')
        _email_icon = solstice_resource.icon('message')
        _documentation_icon = solstice_resource.icon('documentation')
        _production_icon = solstice_resource.icon('production')

        self.doc_action = QAction(_documentation_icon, 'Solstice Documentation', self, statusTip='Open Solstice Documentation webpage', triggered=self._on_open_solstice_documentation)
        self.web_action = QAction(_solstice_icon, 'Solstice Web', self, statusTip='Open Solstice Official webpage', triggered=self._on_open_solstice_web)
        self.project_action = QAction(_artella_icon, 'Solstice Artella Project', self, statusTip='Open Solstice Artella project webpage', triggered=self._on_open_solstice_artella_project)
        self.email_action = QAction(_email_icon, 'Send Email', self, statusTip='Send Email to Solstice TD team', triggered=self._on_send_email)
        self.production_action = QAction(_production_icon, 'Solstice Production Tracker', self, statusTip='Open Solstice Production Tracker', triggered=self._on_open_solstice_production_tracker)
        self.tray_icon_menu = QMenu(self)
        for action in [self.doc_action, self.web_action, self.project_action, self.email_action, self.production_action]:
            self.tray_icon_menu.addAction(action)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._solstice_tools_icon)
        self.tray_icon.setToolTip('Solstice Tools')
        self.tray_icon.setContextMenu(self.tray_icon_menu)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise OSError('Tray Icon is not available!')

        self.tray_icon.show()

    def show_message(self, title, msg):
        try:
            self.tray_icon.showMessage(title, msg, self._solstice_tools_icon)
        except Exception:
            self.tray_icon.showMessage(title, msg)

    @staticmethod
    def _on_open_solstice_web():
        sp.open_solstice_web()

    @staticmethod
    def _on_send_email():
        sp.send_email()

    @staticmethod
    def _on_open_solstice_documentation():
        sp.open_artella_documentation()

    @staticmethod
    def _on_open_solstice_artella_project():
        sp.open_artella_project()

    @staticmethod
    def _on_open_solstice_production_tracker():
        sp.open_production_tracker()
