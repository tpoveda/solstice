#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions and classes to create message boxes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.gui import animations
from solstice.pipeline.resources import resource


class MessageBox(QDialog, object):
    def __init__(self, parent=None, width=None, height=None, enable_input_edit=False, enable_dont_show_checkbox=False):
        super(MessageBox, self).__init__(parent)

        self.setObjectName('messageBox')

        self._frame = None
        self._animation = None
        self._dont_show_checkbox = False
        self._clicked_button = None
        self._clicked_standard_button = None

        self.setMinimumWidth(width or 320)
        self.setMinimumHeight(height or 220)

        self._header = QFrame(self)
        self._header.setFixedHeight(46)
        self._header.setObjectName("messageBoxHeaderFrame")
        self._header.setStyleSheet("background-color: rgb(0,0,0,0);")
        self._header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._icon = QLabel(self._header)
        self._icon.hide()
        self._icon.setFixedWidth(32)
        self._icon.setFixedHeight(32)
        self._icon.setScaledContents(True)
        self._icon.setAlignment(Qt.AlignTop)
        self._icon.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self._title = QLabel(self._header)
        self._title.setObjectName("messageBoxHeaderLabel")
        self._title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        horzontal_layout = QHBoxLayout(self._header)
        horzontal_layout.setContentsMargins(15, 7, 15, 10)
        horzontal_layout.setSpacing(10)
        horzontal_layout.addWidget(self._icon)
        horzontal_layout.addWidget(self._title)

        self._header.setLayout(horzontal_layout)

        body_layout = QVBoxLayout(self)

        self._body = QFrame(self)
        self._body.setObjectName("messageBoxBody")
        self._body.setLayout(body_layout)

        self._message = QLabel(self._body)
        self._message.setWordWrap(True)
        self._message.setMinimumHeight(15)
        self._message.setAlignment(Qt.AlignLeft)
        self._message.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body_layout.addWidget(self._message)
        body_layout.setContentsMargins(15, 15, 15, 15)

        if enable_input_edit:
            self._input_edit = QLineEdit(self._body)
            self._input_edit.setObjectName("messageBoxInputEdit")
            self._input_edit.setMinimumHeight(32)
            self._input_edit.setFocus()

            body_layout.addStretch(1)
            body_layout.addWidget(self._input_edit)
            body_layout.addStretch(10)

        if enable_dont_show_checkbox:
            msg = "Don't show this message again"
            self._dont_show_checkbox = QCheckBox(msg, self._body)

            body_layout.addStretch(10)
            body_layout.addWidget(self._dont_show_checkbox)
            body_layout.addStretch(2)

        self._button_box = QDialogButtonBox(None, Qt.Horizontal, self)
        self._button_box.clicked.connect(self._clicked)
        self._button_box.accepted.connect(self._accept)
        self._button_box.rejected.connect(self._reject)

        vertical_layout = QVBoxLayout(self)
        vertical_layout.setContentsMargins(0, 0, 0, 0)

        vertical_layout.addWidget(self._header)
        vertical_layout.addWidget(self._body)
        body_layout.addWidget(self._button_box)

        self.setLayout(vertical_layout)
        self.updateGeometry()

    @staticmethod
    def input(parent, title, text, input_text='', width=None, height=None, buttons=None, header_icon=None, header_color=None):
        """
        Creates a single text message box
        :param parent: QWidget
        :param title: str
        :param text: str
        :param input_text: str
        :param width: int
        :param height: int
        :param buttons: list(QMessageBox.StandardButton)
        :param header_icon: str
        :param header_color: str
        """

        buttons = buttons or QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        dialog = create_message_box(parent, title, text, width=width, height=height, buttons=buttons, header_icon=header_icon, header_color=header_color, enable_input_edit=True)
        dialog.set_input_text(input_text)
        dialog.exec_()
        clicked_btn = dialog.clicked_standard_button()

        return dialog.input_text(), clicked_btn

    @staticmethod
    def question(parent, title, text, width=None, height=None, buttons=None, header_icon=None, header_color=None, enable_dont_show_checkbox=False):
        """
        Open a question message box with the given options
        :param parent: QWidget
        :param title: str
        :param text: str
        :param width: int
        :param height: int
        :param buttons: list(QMessage.StandardButton)
        :param header_icon: str
        :param header_color: str
        :param enable_dont_show_checkbox: bool
        """

        buttons = buttons or QDialogButtonBox.Yes | QDialogButtonBox.No | QDialogButtonBox.Cancel
        clicked_btn = show_message_box(parent, title, text, width=width, height=height, buttons=buttons, header_icon=header_icon, header_color=header_color, enable_dont_show_checkbox=enable_dont_show_checkbox)

        return clicked_btn

    @staticmethod
    def warning(parent, title, text, width=None, height=None, buttons=None, header_icon=None, header_color='rgb(250, 160, 0)', enable_dont_show_checkbox=False, force=False):
        """
        Open a warning message box with the given options
        :param parent: QWidget
        :param title: str
        :param text: str
        :param width: int
        :param height: int
        :param buttons: list(QMessage.StandardButtons)
        :param header_icon: str
        :param header_color: str
        :param enable_dont_show_checkbox: bool
        :param force: bool
        """

        buttons = buttons or QDialogButtonBox.Yes | QDialogButtonBox.No
        clicked_btn = show_message_box(parent, title, text, width=width, height=height, buttons=buttons, header_icon=header_icon, header_color=header_color, enable_dont_show_checkbox=enable_dont_show_checkbox, force=force)

        return clicked_btn

    @staticmethod
    def critical(parent, title, text, width=None, height=None, buttons=None, header_icon=None, header_color='rgb(250, 160, 0)'):
        """
        Open a critical message box with the given options
        :param parent: QWidget
        :param title: str
        :param text: str
        :param width: int
        :param height: int
        :param buttons: list(QMessage.StandardButtons)
        :param header_icon: str
        :param header_color: str
        """

        buttons = buttons or QDialogButtonBox.Ok
        clicked_btn = show_message_box(parent, title, text, width=width, height=height, buttons=buttons, header_icon=header_icon, header_color=header_color)

        return clicked_btn


    def updateGeometry(self):
        """
        Updates the geometry to be in the center of its parent
        """

        frame = self._frame
        if frame:
            frame.setGeometry(self._frame.parent().geometry())
            frame.move(0, 0)
            geometry = self.geometry()
            center_point = frame.geometry().center()
            geometry.moveCenter(center_point)
            geometry.setY(geometry.y() - 50)
            self.move(geometry.topLeft())

    def eventFilter(self, obj, event):
        """
        Updates the geometry when the parent widget chagnes size
        :param obj: QWidget
        :param event: QEvent
        """

        if event.type() == QEvent.Resize:
            self.updateGeometry()
        return super(MessageBox, self).eventFilter(obj, event)

    def showEvent(self, event):
        """
        Fade in the dailog on show
        :param event: QEvent
        """

        self.updateGeometry()
        self.fade_in()

    def exec_(self):
        """
        Shows the dialgo as a modal dialog
        """

        super(MessageBox, self).exec_()
        return self.clicked_index()

    def button_box(self):
        """
        Returns the button box widget for the dialog
        :return: QDialogButtonBox
        """

        return self._button_box

    def clicked_button(self):
        """
        Returns the button that was clicked
        :return: QPushButton | None
        """

        return self._clicked_button

    def clicked_standard_button(self):
        """
        Returns the button that was clicked by the user
        :return: QMessageBox.StandardButton | None
        """

        return self._clicked_standard_button

    def is_dont_show_checkbox_checked(self):
        """
        Returns the checked state of teh Dont show again checkbox
        :return: bool
        """

        if self._dont_show_checkbox:
            return self._dont_show_checkbox.isChecked()

        return False

    def clicked_index(self):
        """
        Returns the button that was clicked by its index
        :return: int or None
        """

        for i, btn in enumerate(self.button_box().buttons()):
            if btn == self.clicked_button():
                return i

    def add_button(self, *args):
        """
        Creates a button with the given arguments
        :param args:
        """

        self.button_box().addButton(*args)

    def set_pixmap(self, pixmap):
        """
        Set the pixmap for the message box
        :param pixmap: QPixmap
        """

        self._icon.setPixmap(pixmap)
        self._icon.show()

    def set_header_color(self, color):
        """
        Sets the header color for the message box
        :param color: str
        """

        self.header().setStyleSheet('background-color:' + color)

    def set_buttons(self, buttons):
        """
        Set the buttons to be displayed in message box
        :param buttons: QMessageBox.StandardButton
        """

        self.button_box().setStandardButtons(buttons)

    def set_text(self, text):
        """
        Set the text message to be displayed
        :param text: str
        """

        text = str(text)
        self._message.setText(text)

    def header(self):
        """
        Returns the header frame
        :return: QFrame
        """

        return self._header

    def set_title_text(self, text):
        """
        Set the title text to be displayed
        :param text: str
        """

        self._title.setText(text)

    def input_text(self):
        """
        Returns the text that the user has given in the input edit
        :return: str
        """

        return self._input_edit.text()

    def set_input_text(self, text):
        """
        Sets teh input text
        :param text: str
        """

        self._input_edit.setText(text)

    def fade_in(self, duration=200):
        """
        Fdae in the dialog using the opacity effect
        :param duration: int
        :return: QPropertyAnimation
        """

        if self._frame:
            self._animation = animations.fade_in_widget(widget=self._frame, duration=duration)

        return self._animation

    def fade_out(self, duration=200):
        """
        Fade out the dialog using the opacity effect
        :param duration: int
        :return: QPropertyAnimation
        """

        if self._frame:
            self._animation = animations.fade_out_widget(widget=self._frame, duration=duration)

        return self._animation

    def _clicked(self, btn):
        """
        Triggered when the user clicks a button
        :param btn: QPushButton
        """

        self._clicked_button = btn
        self._clicked_standard_button = self.button_box().standardButton(btn)

    def _accept(self):
        """
        Triggered when the DialogButtonBox has been accepted
        """

        animation = self.fade_out()
        if animation:
            animation.finished.connect(self._on_accept_animation_finished)
        else:
            self._on_accept_animation_finished()

    def _reject(self):
        """
        Triggered when the DialogButtonBox has been rejected
        """

        animation = self.fade_out()
        if animation:
            animation.finished.connect(self._on_reject_animation_finished)
        else:
            self._on_reject_animation_finished()

    def _on_accept_animation_finished(self):
        """
        Triggered when the animation has finished on accepted
        """

        parent = self._frame or self
        parent.close()
        self.accept()


    def _on_reject_animation_finished(self):
        """
        Triggered when the animation has finished on rejected
        """

        parent = self._frame or self
        parent.close()
        self.reject()


def create_message_box(parent, title, text, width=None, height=None, buttons=None, header_icon=None, header_color=None, enable_input_edit=False, enable_dont_show_checkbox=False):
    """
    Opens a question message box with the given options
    :param parent: QWidget
    :param title: str
    :param text: str
    :param width: int
    :param height: int
    :param buttons: list(QMessageBox.StandardButton)
    :param header_icon: QIcon
    :param header_color: str
    :param enable_input_edit: str
    :param enable_dont_show_checkbox: bool
    :return: MessageBox
    """

    mb = MessageBox(parent, width=width, height=height, enable_input_edit=enable_input_edit, enable_dont_show_checkbox=enable_dont_show_checkbox)
    mb.set_text(text)
    buttons = buttons or QDialogButtonBox.Ok
    mb.set_buttons(buttons)
    if header_icon:
        p = resource.pixmap(header_icon)
        mb.set_pixmap(p)

    mb.setWindowTitle(title)
    mb.set_title_text(title)

    return mb


def show_message_box(parent, title, text, width=None, height=None, buttons=None, header_icon=None, header_color=None, enable_dont_show_checkbox=False, force=False):
    """
    Opens a question message box with the given options
    :param parent: QWidget
    :param title: str
    :param text: str
    :param width: int
    :param height: int
    :param buttons: list(QMessaegBox.StandardButton)
    :param header_icon: str
    :param header_color: str
    :param enable_dont_show_checkbox: bool
    :param force: bool
    :return: MessageBox
    """

    mb = create_message_box(parent, title, text, width=width, height=height, buttons=buttons, header_icon=header_icon, header_color=header_color, enable_dont_show_checkbox=enable_dont_show_checkbox)
    mb.exec_()
    mb.close()
    clicked_btn = mb.clicked_standard_button()

    return clicked_btn


