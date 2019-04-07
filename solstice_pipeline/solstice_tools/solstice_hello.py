#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_hello.py
# by Tomas Poveda
# Tool that that helps user to start working with Solstice Tools
# ______________________________________________________________________
# ==================================================================="""

import sys

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_pipeline import solstice_tools
from solstice_pipeline.solstice_gui import solstice_dialog, solstice_animations
from solstice_pipeline.solstice_utils import solstice_python_utils
from solstice_pipeline.resources import solstice_resource


class SolsticeHelloDialog(solstice_dialog.Dialog, object):

    name = 'SolsticeHello'
    title = 'Solstice Tools - Hello'
    version = '1.0'
    docked = False

    def __init__(self, **kwargs):

        self._max_pages = 3
        self._offset = 0

        super(SolsticeHelloDialog, self).__init__(**kwargs)

    def custom_ui(self):
        super(SolsticeHelloDialog, self).custom_ui()

        self.resize(685, 290)

        self.logo_view.setVisible(False)
        self.main_title.setVisible(False)
        self.ui = solstice_tools.load_tool_ui(self.name)
        self.main_layout.addWidget(self.ui)

        logo_gif = solstice_resource.get('icons', 'solstice_logo.gif')
        self.gif_file = open(logo_gif, 'rb').read()
        self.gif_byte_array = QByteArray(self.gif_file)
        self.gif_buffer = QBuffer(self.gif_byte_array)
        self.logo = QMovie()
        self.logo.setDevice(self.gif_buffer)
        self.logo.setCacheMode(QMovie.CacheAll)
        self.logo.setScaledSize(QSize(60, 60))
        self.logo.setSpeed(100)
        self.logo.jumpToFrame(0)
        self.logo.start()
        self.ui.solstice_logo.setMovie(self.logo)
        self.tab_opacity_effect = QGraphicsOpacityEffect(self)
        self.tab_opacity_effect.setOpacity(0)
        self.ui.pages_stack.setGraphicsEffect(self.tab_opacity_effect)

        self.ui.close_btn.clicked.connect(self.fade_close)
        self.ui.right_btn.clicked.connect(lambda: self._on_button_press(+1))
        self.ui.left_btn.clicked.connect(lambda: self._on_button_press(-1))
        self.ui.page_btn_0.clicked.connect(lambda: self.set_index(0))
        self.ui.page_btn_1.clicked.connect(lambda: self.set_index(1))
        self.ui.page_btn_2.clicked.connect(lambda: self.set_index(2))
        self.ui.page_btn_3.clicked.connect(lambda: self.set_index(3))
        self.ui.documentation_btn.clicked.connect(lambda : solstice_python_utils.open_web('https://tpoveda.github.io/solstice/'))
        self.ui.changelog_btn.clicked.connect(self.open_chagelog)

        self.ui.label_4.setVisible(False)
        self.ui.hotkey.setVisible(False)

        self.set_index(0)

        current_version = sp.get_version()
        self.ui.version_lbl.setText('v{}'.format(current_version))

        system = sys.platform
        print(system)
        if system == 'darwin':
            self.ui.hotkey.setText('SHIFT + TAB')
        else:
            self.ui.hotkey.setText('CTRL + TAB')

    def mousePressEvent(self, event):
        self._offset = event.pos()

    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self._offset.x()
        y_w = self._offset.y()
        self.move(x - x_w, y - y_w)

    def set_index(self, index):
        solstice_animations.fade_animation(start='current', end=0, duration=400, object=self.tab_opacity_effect)

        if index <= 0:
            index = 0
        if index >= self._max_pages:
            index = self._max_pages

        if index == 0:
            self.ui.page_btn_0.setChecked(True)
        elif index == 1:
            self.ui.page_btn_1.setChecked(True)
        elif index == 2:
            self.ui.page_btn_2.setChecked(True)
        elif index == 3:
            self.ui.page_btn_3.setChecked(True)

        self.props_timer = QTimer(singleShot=True)
        self.props_timer.timeout.connect(self._on_fade_up_tab)
        self.props_timer.timeout.connect(lambda: self.ui.pages_stack.setCurrentIndex(index))
        self.props_timer.start(450)

        prev_text = 'Previous'
        next_text = 'Next'
        skip_text = 'Skip'
        close_text = 'Finish'

        if index == 0:
            self.ui.left_btn.setText(skip_text)
        elif index <= self._max_pages - 1:
            self.ui.left_btn.setText(prev_text)
            self.ui.right_btn.setText(next_text)
        elif index == self._max_pages:
            self.ui.left_btn.setText(prev_text)
            self.ui.right_btn.setText(close_text)

    def increment_index(self, input):
        current = self.ui.pages_stack.currentIndex()
        self.set_index(current + input)

    def launch_solstice_tools(self):
        self.fade_close()

    def open_chagelog(self):
        from solstice_pipeline.solstice_tools import solstice_changelog
        solstice_changelog.run()

    def _on_fade_up_tab(self):
        solstice_animations.fade_animation(start='current', end=1, duration=400, object=self.tab_opacity_effect)

    def _on_button_press(self, input):
        current = self.ui.pages_stack.currentIndex()
        action = 'flip'
        if current == 0:
            if input == -1:
                action = 'close'
        elif current == self._max_pages:
            if input == 1:
                action = 'close'
        if action == 'flip':
            self.increment_index(input)
        elif action == 'close':
            self.launch_solstice_tools()


class SolsticeHelloWidget(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeHelloWidget, self).__init__(parent)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        self.setLayout(base_layout)

        main_frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        main_frame.setLayout(frame_layout)
        base_layout.addWidget(main_frame)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 0)
        top_layout.setSpacing(0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        test_btn = QPushButton('TEST')
        main_layout.addWidget(test_btn)


def run():
    hello_dialog = SolsticeHelloDialog()
    hello_dialog.exec_()
