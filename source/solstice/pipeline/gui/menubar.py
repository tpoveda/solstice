#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom toolbar
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import icon


class MenuBarWidget(QToolBar, object):

    DEFAULT_EXPANDED_HEIGHT = 34
    DEFAULT_COLLAPSED_HEIGHT = 10

    def __init__(self, parent=None):
        super(MenuBarWidget, self).__init__(parent=parent)

        self._dpi = 1
        self._is_expanded = True
        self._expand_height = self.DEFAULT_COLLAPSED_HEIGHT
        self._collapsed_height = self.DEFAULT_COLLAPSED_HEIGHT

    def setFixedHeight(self, value):
        """
        Overrides this base setFixedHeight() function to also set the height for all child widgets
        :param value: bool
        """

        self.set_children_height(value)
        super(MenuBarWidget, self).setFixedHeight(value)

    def dpi(self):
        """
        Returns the zoom multiplier
        :return: float
        """

        return self._dpi

    def set_dpi(self, dpi):
        """
        Sets the zoom multiplier
        :param dpi: float
        """

        self._dpi = dpi

    def is_expanded(self):
        """
        Returns whether the menuBar is expanded or not
        :return: bool
        """

        return self._is_expanded

    def expand_height(self):
        """
        Returns the height of widget when expanded
        :return: int
        """

        return int(self._expand_height * self.dpi())

    def collapse_height(self):
        """
        Returns the height of the widget when collapsed
        :return: int
        """

        return int(self._collapsed_height * self.dpi())

    def set_children_hidden(self, value):
        """
        Set all child widgets to hidden
        :param value: bool
        """

        for w in self.widgets():
            w.setHidden(value)

    def set_children_height(self, height):
        """
        Set the height of all the child widgets to the given height
        :param height: int
        """

        for w in self.widgets():
            w.setFixedHeight(height)

    def expand(self):
        """
        Expand the MenBar to the expandHeight
        """

        self._is_expanded = True
        height = self.expand_height()
        self.setFixedHeight(height)
        self.set_children_hidden(False)
        self.setIconSize(QSize(height, height))

    def collapse(self):
        """
        Collapse the MenuBar to the collapseHeight
        """

        self._is_expanded = False
        height = self.collapse_height()
        self.setFixedHeight(height)
        self.set_children_height(0)
        self.set_children_hidden(True)
        self.setIconSize(QSize(0, 0))

    def set_icon_color(self, color):
        """
        Sets the icon colors to the current foregroundRole
        :param color: QColor
        """

        for action in self.actions():
            ic = action.icon()
            ic = icon.Icon(ic)
            ic.set_color(color)
            action.setIcon(ic)

    def widgets(self):
        """
        Returns all the widgets that are a child of the MenuBar
        :return: list(QWidget)
        """

        widgets = list()

        for i in range(self.layout().count()):
            w = self.layout().itemAt(i).widget()
            if isinstance(w, QWidget):
                widgets.append(w)

        return widgets

    def actions(self):
        """
        Returns all the actions that are a child of the MenuBar
        :return: list(QAction)
        """

        actions = list()

        for child in self.children():
            if isinstance(child, QAction):
                actions.append(child)

        return actions

    def find_action(self, text):
        """
        Find the action with the given text
        :param text: str
        :return: QAction or None
        """

        for child in self.children():
            if isinstance(child, QAction):
                if child.text() == text:
                    return child

    def find_tool_button(self, text):
        """
        Find the QToolButton with the given text
        :param text: str
        :return: QToolButton or None
        """

        for child in self.children():
            if isinstance(child, QAction):
                if child.text() == text:
                    return self.widgetForAction(child)

    def insertAction(self, before, action):
        """
        Override base insertAction() function to suppo0rt the before argument as string
        :param before: QAction or str
        :param action: QAction
        :return: QAction
        """

        action.setParent(self)

        if isinstance(before, basestring):
            before = self.find_action(before)

        action = super(MenuBarWidget, self).insertAction(before, action)

        return action
