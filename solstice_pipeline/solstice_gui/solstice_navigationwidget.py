#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_navigationwidget.py
# by Tomas Poveda
# Module that contains class to create a navigation folder widget
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from resources import solstice_resource


class NavigationWidget(QWidget, object):
    """
    This widget keeps track of the current location withing a list and
    emits signals whenever the user navigates via one of the buttons
    """

    navigate = Signal(object)
    home_clicked = Signal()

    class _DestinationInfo(object):
        """
        Container class used to keep track of information about a destination
        """

        def __init__(self, label, destination):
            self.label = label
            self.destination = destination

    def __init__(self, parent=None):
        super(NavigationWidget, self).__init__(parent=parent)

        self._destinations = list()
        self._current_id = 0

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.mainWidget = solstice_resource.gui('navigation_widget')
        self.mainWidget.nav_home_btn.clicked.connect(self.home_clicked)

        main_layout.addWidget(self.mainWidget)

        self._update_ui()

    def _update_ui(self):
        pass
