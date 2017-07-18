#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: sPickerScene.py
by Tomás Poveda
Solstice Short Film Project
______________________________________________________________________
Customized picker for Solstice characters
______________________________________________________________________
==================================================================="""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtGui import *
    from PySide.QtCore import *

class solstice_pickerScene(QGraphicsScene, object):

    """
    Scene for the picker
    """

    __DEFAULT_SCENE_WIDTH__ = 100
    __DEFAULT_SCENE_HEIGHT__ = 200

    def __init__(self, parent=None):
        super(solstice_pickerScene, self).__init__(parent=parent)

        self.setDefaultSize()

    def setSize(self, width, height):
        self.setSceneRect(-width/2, -height/2, width, height)

    def setDefaultSize(self):
        return self.setSize(self.__DEFAULT_SCENE_WIDTH__, self.__DEFAULT_SCENE_HEIGHT__)

    def getBoundingRect(self):
        return self.itemsBoundingRect()