#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom QWidget used as container for other widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtWidgets import *


class ContainerWidget(QWidget, object):

    def __init__(self, parent=None):
        super(ContainerWidget, self).__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.containedWidget = None

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
