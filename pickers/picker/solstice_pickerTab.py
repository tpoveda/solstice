#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: solstice_pickerTab.py
by Tomás Poveda
Custom tabs used by the picker of Solstice Short Film
______________________________________________________________________
Tab class to be used in the pickers
______________________________________________________________________
==================================================================="""

# Import PySide modules
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

# Import standard Python modules
import os

class solstice_pickerTab(QWidget, object):
    def __init__(self, parent=None):

        """
        Constructor
        """

        super(solstice_pickerTab, self).__init__(parent)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

        self._bgImage = QLabel()
        self._bgImage.setParent(self)

        self.initUI()

    def initUI(self):

        """
        Override this method to add the UI of the picker tab
        """

        pass

    def setBackgroundImage(self, imagePath):

        """
        Sets the background image for the tab picker
        """

        if os.path.isfile(imagePath):
            bgPixmap = QPixmap(imagePath)
            self._bgImage.setMinimumWidth(bgPixmap.size().width())
            self._bgImage.setMinimumHeight(bgPixmap.size().height())
            self._bgImage.setMaximumWidth(bgPixmap.size().width())
            self._bgImage.setMaximumHeight(bgPixmap.size().height())
            self._bgImage.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self._bgImage.setPixmap(bgPixmap)