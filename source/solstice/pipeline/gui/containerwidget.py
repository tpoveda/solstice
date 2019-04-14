#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_containerwidget.py
# by Tomas Poveda
# Custom QWidget used as container for other widgets
# ______________________________________________________________________
# ==================================================================="""

from pipeline.externals.solstice_qt.QtCore import *
from pipeline.externals.solstice_qt.QtWidgets import *
from pipeline.externals.solstice_qt.QtGui import *


class ContainerWidget(QWidget, object):
    """
    Basic widget used a
    """

    def __init__(self, parent=None):
        super(ContainerWidget, self).__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.containedWidget = None

    # region Functions
    def set_contained_widget(self, widget):
        """
        Sets the current contained widget for this container
        :param widget: QWidget
        """

        self.containedWidget = widget
        if widget:
            widget.setParent(self)
            self.layout().addWidget(widget)

    def clone_and_pass_contained_widget(self):
        """
        Returns a clone of this ContainerWidget
        :return: ContainerWidget
        """

        cloned = ContainerWidget(self.parent())
        cloned.set_contained_widget(self.containedWidget)
        self.set_contained_widget(None)
        return cloned
    # endregion
