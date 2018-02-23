#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ==================================================================
Script Name: sPickerView.py
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
    from PySide2.QtSvg import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtSvg import *
    from shiboken import wrapInstance

import solstice_pickerScene as scene

class solstice_pickerView(QGraphicsView, object):

    """
    View of the picker
    """

    def __init__(self, dataPath=None, imagePath=None, namespace='', parent=None):
        super(solstice_pickerView, self).__init__(parent=parent)

        self.setScene(scene.solstice_pickerScene(dataPath=dataPath, namespace=namespace))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setResizeAnchor(self.AnchorViewCenter)
        self.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Scale view in Y negative so position Y values works similar as Maya
        #self.scale(1, -1)

        brush = QBrush(QColor(70,70,70,255))
        self.setBackgroundBrush(brush)
        self._backgroundImage = None
        if imagePath:
            self.setBackgroundImage(imagePath)

    def backgroundImage(self):
        return self._backgroundImage

    def setBackgroundImage(self, imagePath):
        if not imagePath:
            return

        self._backgroundImage = QGraphicsSvgItem(imagePath)
        self._backgroundImage.setZValue(-1)
        self.scene().addItem(self._backgroundImage)

        width = self._backgroundImage.boundingRect().size().width()
        height = self._backgroundImage.boundingRect().size().height()

        print('width: ', width)
        print('height: ', height)

        self.scene().setSize(width, height)
        self.fitSceneToContent()

        self._backgroundImage.moveBy(-width*0.5, -height*0.5)

    def fitSceneToContent(self, keepAspectRatio=False):

        if keepAspectRatio:
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        else:
            self.fitInView(self.scene().sceneRect())

    def getCenterPos(self):
        return self.mapToScene(QPoint(self.width()/2, self.height()/2))

    def drawBackground(self, painter ,rect):
        result = QGraphicsView.drawBackground(self, painter, rect)
        # if not self._backgroundImage:
        #     return result
        # painter.drawImage(self.sceneRect(), self._backgroundImage, QRectF(self._backgroundImage.rect()))

    def clear(self):
        oldScene = self.scene()
        self.setScene(scene.solstice_pickerScene())
        oldScene.deleteLater()

    def resizeEvent(self, *args, **kwargs):
        self.fitSceneToContent()
        return QGraphicsView.resizeEvent(self, *args, **kwargs)