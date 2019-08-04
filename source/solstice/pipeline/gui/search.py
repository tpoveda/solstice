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

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from solstice.pipeline.gui import icon, color, buttons
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


class SearchFindWidget(QWidget, object):

    textChanged = Signal(str)
    editingFinished = Signal(str)
    returnPressed = Signal()

    def __init__(self, parent=None):
        super(SearchFindWidget, self).__init__(parent=parent)

        self.text = ''
        self._placeholder_text = ''

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self._search_line = QLineEdit(self)
        self._search_menu = QMenu()
        self._search_menu.addAction('Test')

        icon_size = self.style().pixelMetric(QStyle.PM_SmallIconSize)

        self._clear_btn = buttons.IconButton('delete', icon_padding=2, parent=self)
        self._clear_btn.setIconSize(QSize(icon_size, icon_size))
        self._clear_btn.setFixedSize(QSize(icon_size, icon_size))
        self._clear_btn.hide()

        self._search_btn = buttons.IconButton('search', icon_padding=2, parent=self)
        self._search_btn.setIconSize(QSize(icon_size, icon_size))
        self._search_btn.setFixedSize(QSize(icon_size, icon_size))
        # self._search_btn.setStyleSheet('border: none;')
        # self._search_btn.setPopupMode(QToolButton.InstantPopup)
        self._search_btn.setEnabled(True)

        self._search_line.setStyleSheet(
            """
            QLineEdit { padding-left: %spx; padding-right: %spx; border-radius:10px; border:2px; border-color:red; } 
            """ % (self._search_button_padded_width(), self._clear_button_padded_width())
        )
        self._search_line.setMinimumSize(
            max(self._search_line.minimumSizeHint().width(), self._clear_button_padded_width() + self._search_button_padded_width()),
            max(self._search_line.minimumSizeHint().height(), max(self._clear_button_padded_width(), self._search_button_padded_width()))
        )

        main_layout.addWidget(self._search_line)

        self._search_line.setFocus()

        self._search_line.textChanged.connect(self.textChanged)
        self._search_line.textChanged.connect(self.set_text)
        # self._search_line.editingFinished.connect(self.editingFinished)
        # self._search_line.returnPressed.connect(self.returnPressed)
        self._clear_btn.clicked.connect(self.clear)
        self._search_btn.clicked.connect(self._popup_menu)

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

    text = property(get_text, set_text)

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            enabled = self.isEnabled()
            self._search_btn.setEnabled(enabled and self._search_menu)
            self._search_line.setEnabled(enabled)
            self._clear_btn.setEnabled(enabled)
        super(SearchFindWidget, self).changeEvent(event)

    def resizeEvent(self, event):
        if not (self._clear_btn and self._search_line):
            return
        super(SearchFindWidget, self).resizeEvent(event)
        x = self.width() - self._clear_button_padded_width() * 0.85
        y = (self.height() - self._clear_btn.height()) * 0.5
        self._clear_btn.move(x - 3, y)
        self._search_btn.move(self._search_line_frame_width() * 2, (self.height() - self._search_btn.height()) * 0.5)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
        super(SearchFindWidget, self).keyPressEvent(event)

    def get_text(self):
        if not self._search_line:
            return ''
        return self._search_line.text()

    def set_text(self, text):
        if not (self._clear_btn and self._search_line):
            return

        self._clear_btn.setVisible(not (len(text) == 0))
        if text != self.get_text():
            self._search_line.setText(text)

    def get_placeholder_text(self):
        if not self._search_line:
            return ''

        return self._search_line.text()

    def set_placeholder_text(self, text):
        if not self._search_line:
            return
        self._search_line.setPlaceholderText(text)

    def get_menu(self):
        search_icon = resource.icon('search')
        self._search_btn.setIcon(search_icon)
        self._search_btn.setEnabled(self.isEnabled() and self._menu)

    def set_focus(self, reason=Qt.OtherFocusReason):
        if self._search_line:
            self._search_line.setFocus(reason)
        else:
            self.setFocus(Qt.OtherFocusReason)

    def clear(self):
        if not self._search_line:
            return
        self._search_line.clear()
        self.set_focus()

    def select_all(self):
        if not self._search_line:
            return
        self._search_line.selectAll()

    def _search_line_frame_width(self):
        return self._search_line.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

    def _clear_button_padded_width(self):
        return self._clear_btn.width() + self._search_line_frame_width() * 2

    def _clear_button_padded_height(self):
        return self._clear_btn.height() + self._search_line_frame_width() * 2

    def _search_button_padded_width(self):
        return self._search_btn.width() + self._search_line_frame_width() * 2

    def _search_button_padded_height(self):
        return self._search_btn.height() + self._search_line_frame_width() * 2

    def _popup_menu(self):
        if self._search_menu:
            screen_rect = QApplication.desktop().availableGeometry(self._search_btn)
            size_hint = self._search_menu.sizeHint()
            rect = self._search_btn.rect()
            x = rect.right() - size_hint.width() if self._search_btn.isRightToLeft() else rect.left()
            y = rect.bottom() if self._search_btn.mapToGlobal(QPoint(0,
                                                                     rect.bottom())).y() + size_hint.height() <= screen_rect.height() else rect.top() - size_hint.height()
            point = self._search_btn.mapToGlobal(QPoint(x, y))
            point.setX(max(screen_rect.left(), min(point.x(), screen_rect.right() - size_hint.width())))
            point.setY(point.y() + 1)
            print('pop up on {}'.format(point))
            self._search_menu.popup(point)

