#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic search widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from functools import partial

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtGui import *

from solstice.pipeline.gui import icon, color
from solstice.pipeline.resources import resource


class SearchWidget(QLineEdit, object):

    searchChanged = Signal()

    def __init__(self, *args, **kwargs):
        super(SearchWidget, self).__init__(*args, **kwargs)

        self._data = None
        self._space_operator = 'and'
        self._icon_padding = 6

        self.setPlaceholderText('Search')
        self.setFrame(False)

        self._icon_btn = QPushButton(self)
        self._icon_btn.setStyleSheet('border: none;')
        ic = resource.icon('search')
        self.set_icon(ic)

        self._clear_btn = QPushButton(self)
        self._clear_btn.setCursor(Qt.ArrowCursor)
        ic = resource.icon('delete')
        self._clear_btn.setIcon(ic)
        self._clear_btn.setToolTip('Clar all search text')
        self._clear_btn.setStyleSheet('border: none;')

        self.textChanged.connect(self._on_text_changed)
        self._icon_btn.clicked.connect(self._on_search)
        self._clear_btn.clicked.connect(self._on_clear)

        self.update()

    def update(self):
        # self.update_icon_color()
        self.update_clear_button()

    def resizeEvent(self, event):
        """
        Reimplement so icons maintian the same height as the widget
        :param event: QResizeEvent
        """

        super(SearchWidget, self).resizeEvent(event)
        self.setTextMargins(self.height(), 0, 0, 0)
        size = QSize(self.height(), self.height())
        self._icon_btn.setIconSize(size)
        self._icon_btn.setFixedSize(size)
        self._clear_btn.setIconSize(size)
        x = self.width() - self.height()
        self._clear_btn.setGeometry(x, 0, self.height(), self.height())

    def keyPressEvent(self, event):
        super(SearchWidget, self).keyPressEvent(event)

        if event.key() == Qt.Key_Escape:
            self._on_clear()

    def contextMenuEvent(self, event):
        """
        Triggered when the user right click on the search widget
        :param event: QEvent
        """

        self._show_context_menu()

    def data(self):
        """
        Returns the data for the search widget
        :return: SearchData
        """

        return self._data

    def set_data(self, data):
        """
        Sets the data for the search widget
        :param data: SearchData
        """

        self._data = data

    def space_operator(self):
        """
        Returns the space operator for the search widget
        :return: str
        """

        return self._space_operator

    def set_space_operator(self, operator):
        """
        Sets the space operator for the search widget
        :param operator: str
        """

        self._space_operator = operator
        self.search()

    def search(self):
        """
        Run the search query on the data set
        """

        self.update_clear_button()
        self.searchChanged.emit()

    def query(self):
        """
        Get the query used for the data set
        :return: dict
        """

        text = str(self.text())

        filters = list()
        for filter_ in text.split(' '):
            if filter_.split():
                filters.append(('*', 'contains', filter_))

        unique_name = 'searchWidget' + str(id(self))

        return {
            'name': unique_name,
            'operator': self.space_operator(),
            'filters': filters
        }

    def set_icon(self, icon):
        """
        Sets the icon for the search widget
        :param icon: QIcon
        :return: None
        """

        self._icon_btn.setIcon(icon)

    def set_icon_color(self, color):
        """
        Sets the icon color for the search widget icon
        :param color: QColor
        """

        ic = self._icon_btn.icon()
        ic = icon.Icon(ic)
        ic.set_color(color)
        self._icon_btn.setIcon(ic)

        ic = self._clear_btn.icon()
        ic = icon.Icon(ic)
        ic.set_color(color)
        self._clear_btn.setIcon(ic)

    def update_icon_color(self):
        """
        Updates the cion colors to the current foregroundRole
        """

        clr = self.palette().color(self.foregroundRole())
        clr = color.Color.from_color(clr)
        self.set_icon_color(clr)

    def update_clear_button(self):
        """
        Updates the clear button depending on the current text
        :return:
        """

        text = self.text()
        if text:
            self._clear_btn.show()
        else:
            self._clear_btn.hide()

    def settings(self):
        """
        Returns a dictionary of the current widget state
        :return: dict
        """

        settings = {
            'text': self.text(),
            'space_operator': self.space_operator()
        }

        return settings

    def set_settings(self, settings):
        """
        Restore the widget state from a setting dictionary
        :param settings: dict
        """

        text = settings.get('text', '')
        self.setText(text)

        space_operator = settings.get('space_operator')
        if space_operator:
            self.set_space_operator(space_operator)

    def _show_context_menu(self):
        """
        Create and show the context menu for the search widget
        :return: QAction
        """

        menu = QMenu(self)

        sub_menu = self.createStandardContextMenu()
        sub_menu.setTitle('Edit')
        menu.addMenu(sub_menu)

        sub_menu = self._create_space_operator_menu(menu)
        menu.addMenu(sub_menu)

        action = menu.exec_(QCursor.pos())

        return action

    def _create_space_operator_menu(self, parent=None):
        """
        Returns the menu for changing the space operator
        :param parent: QMenu
        :return: QMenu
        """

        menu = QMenu(parent)
        menu.setTitle('Space Operator')

        action = QAction(menu)
        action.setText('OR')
        action.setCheckable(True)
        callback = partial(self.set_space_operator, 'or')
        action.triggered.connect(callback)
        if self.space_operator() == 'or':
            action.setChecked(True)
        menu.addAction(action)

        action = QAction(menu)
        action.setText('AND')
        action.setCheckable(True)
        callback = partial(self.set_space_operator, 'and')
        action.triggered.connect(callback)
        if self.space_operator() == 'and':
            action.setChecked(True)
        menu.addAction(action)

        return menu

    def _on_search(self):
        """
        Callback triggered when the user clicks search icon
        """

        if not self.hasFocus():
            self.setFocus()

    def _on_clear(self):
        """
        Callback triggered when the user clicks cross icon
        """
        self.setText('')
        self.setFocus()

    def _on_text_changed(self):
        """
        Callback triggered when the text changes
        """

        self.search()
