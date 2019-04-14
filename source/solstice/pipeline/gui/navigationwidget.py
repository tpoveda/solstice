#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains class to create a navigation folder widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.resources import resource


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

        self.mainWidget = resource.gui('navigation_widget')
        self.mainWidget.nav_home_btn.clicked.connect(self.home_clicked)

        main_layout.addWidget(self.mainWidget)

        self._update_ui()

    def _update_ui(self):
        pass
