#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerButtons.py
by Tomás Poveda
Custom button used by the picker of Solstice Short Film
______________________________________________________________________
Button classes to be used in the pickers
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

import solstice_pickerBaseButton as baseButton

class solstice_circularButton(baseButton.solstice_pickerBaseButton, object):
    def __init__(self, radius=8, parent=None):
        super(solstice_circularButton, self).__init__(parent=parent)

        self._radius = radius

    def radius(self):
        return self._radius

    def setRadius(self, radius):
        self._radius = radius

    def paintBorder(self, painter, x, y, width, height):
        painter.drawEllipse(QRect(x + 1, y + 1, width - 1, height - 1))
        #painter.drawRoundedRect(QRect(x+1, y+1, width-1, height-1), self._radius, self._radius)

    def paintOuter(self, painter, x, y, width, height):
        painter.drawEllipse(QRect(x + 2, y + 2, width - 3, height - 3))
        #painter.drawRoundedRect(QRect(x + 2, y + 2, width - 3, height - 3), self._radius, self._radius)

    def paintInner(self, painter, x, y, width, height):
        painter.drawEllipse(QRect(x + 3, y + 3, width - 5, height - 5))
        #painter.drawRoundedRect(QRect(x + 3, y + 3, width - 5, height - 5), self._radius - 1, self._radius - 1)

class solstice_fkButton(solstice_circularButton, object):
    def __init__(self, parent=None):
        super(solstice_fkButton, self).__init__(parent=parent)

        self.setText('FK')