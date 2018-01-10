#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_splitters.py
# by Tomas Poveda @ Solstice
# Module that contains different splitter wigets
# ______________________________________________________________________
# ==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

class Splitter (QWidget, object):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):

        """
        Basic standard splitter with optional text
        :param str text: Optional text to include as title in the splitter
        :param bool shadow: True if you want a shadow above the splitter
        :param tuple(int) color: Color of the slitter's text
        """

        super (Splitter, self).__init__ ()

        self.setMinimumHeight (2)
        self.setLayout (QHBoxLayout ())
        self.layout ().setContentsMargins (0, 0, 0, 0)
        self.layout ().setSpacing (0)
        self.layout ().setAlignment (Qt.AlignVCenter)

        first_line = QFrame ()
        first_line.setFrameStyle (QFrame.HLine)
        self.layout ().addWidget (first_line)

        main_color = 'rgba(%s, %s, %s, 255)' % color
        shadow_color = 'rgba(45, 45, 45, 255)'

        bottom_border = ''
        if shadow:
            bottom_border = 'border-bottom:1px solid %s;' % shadow_color

        style_sheet = "border:0px solid rgba(0,0,0,0); \
                      background-color: %s; \
                      mayamaya-height: 1px; \
                      %s" % (main_color, bottom_border)

        first_line.setStyleSheet (style_sheet)

        if text is None:
            return

        first_line.setMaximumWidth (5)

        font = QFont ()
        font.setBold (True)

        text_width = QFontMetrics (font)
        width = text_width.width (text) + 6

        label = QLabel ()
        label.setText (text)
        label.setFont (font)
        label.setMaximumWidth (width)
        label.setAlignment (Qt.AlignCenter | Qt.AlignVCenter)

        self.layout ().addWidget (label)

        second_line = QFrame ()
        second_line.setFrameStyle (QFrame.HLine)
        second_line.setStyleSheet (style_sheet)

        self.layout ().addWidget (second_line)


class SplitterLayout (QHBoxLayout, object):
    def __init__(self):

        """
        Basic splitter to separate layouts
        """

        super(SplitterLayout, self).__init__()

        self.setContentsMargins(40, 2, 40, 2)

        splitter = Splitter(shadow=False, color=(60, 60, 60))
        splitter.setFixedHeight(2)

        self.addWidget(splitter)