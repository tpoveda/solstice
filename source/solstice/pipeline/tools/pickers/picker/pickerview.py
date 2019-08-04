#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Picker View Class
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *
from Qt.QtSvg import *

from solstice.pipeline.tools.pickers.picker import scene


class PickerView(QGraphicsView, object):
    def __init__(self, data_path=None, image_path=None, namespace='', parent=None):
        super(PickerView, self).__init__(parent=parent)

        self.setScene(scene.PickerScene(data_path=data_path, namespace=namespace))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setResizeAnchor(self.AnchorViewCenter)
        self.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        brush = QBrush(QColor(70, 70, 70, 255))
        self.setBackgroundBrush(brush)
        self._background_image = None
        if image_path:
            self.background_image = image_path

    def get_background_image(self):
        return self._background_image

    def set_background_image(self, image_path):
        if not image_path:
            return

        self._background_image = QGraphicsSvgItem(image_path)
        self._background_image.setZValue(-1)
        self.scene().addItem(self._background_image)
        width = self._background_image.boundingRect().size().width()
        height = self._background_image.boundingRect().size().height()
        self._background_image.moveBy(-width*0.5, -height*0.5)
        self.scene().set_size(width, height)
        self.fit_scene_to_content()

    background_image = property(get_background_image, set_background_image)

    def drawBackground(self, painter, rect):
        result = QGraphicsView.drawBackground(self, painter, rect)

    def resizeEvent(self, *args, **kwargs):
        self.fit_scene_to_content()
        return QGraphicsView.resizeEvent(self, *args, **kwargs)

    def fit_scene_to_content(self, keep_aspect_ratio=False):
        if keep_aspect_ratio:
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        else:
            self.fitInView(self.scene().sceneRect())

    def get_center_pos(self):
        return self.mapToScene(QPoint(self.width()*0.5, self.height()*0.5))

    def clear(self):
        old_scene = self.scene()
        self.setScene(scene.PickerScene())
        old_scene.deleteLater()