#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_published_info_widget.py
# by Tomas Poveda
# Widget used to show published info in Solstice Pipelinizer Tool
# ______________________________________________________________________
# ==================================================================="""


from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from resources import solstice_resource
from solstice_utils import solstice_qt_utils
from solstice_gui import solstice_splitters

reload(solstice_qt_utils)
reload(solstice_splitters)


class PublishedInfoWidget(QWidget, object):

    _error_pixmap = solstice_resource.pixmap('error', category='icons').scaled(QSize(24, 24))
    _warning_pixmap = solstice_resource.pixmap('warning', category='icons').scaled(QSize(24, 24))
    _ok_pixmap = solstice_resource.pixmap('ok', category='icons').scaled(QSize(24, 24))

    def __init__(self, asset, parent=None):
        super(PublishedInfoWidget, self).__init__(parent=parent)

        self._asset = asset
        self._has_model = True
        self._has_shading = True
        self._has_textures = True

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        self._main_layout.setSpacing(5)
        self.setLayout(self._main_layout)

        asset.is_published()

        self.update_published_info()

    def update_published_info(self):

        solstice_qt_utils.clear_layout_widgets(self._main_layout)

        if self._has_model:
            model_layout = QHBoxLayout()
            model_layout.setContentsMargins(2, 2, 2, 2)
            model_layout.setSpacing(2)
            model_layout.setAlignment(Qt.AlignLeft)
            self._main_layout.addLayout(model_layout)
            self._model_status = QLabel()
            self._model_status.setPixmap(self._error_pixmap)
            model_lbl = QLabel('    MODEL')
            self._model_text = QLabel('')
            model_layout.addWidget(self._model_status)
            model_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            model_layout.addWidget(model_lbl)
            model_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            model_layout.addWidget(self._model_text)

        if self._has_shading:
            shading_layout = QHBoxLayout()
            shading_layout.setContentsMargins(2, 2, 2, 2)
            shading_layout.setSpacing(2)
            shading_layout.setAlignment(Qt.AlignLeft)
            self._main_layout.addLayout(shading_layout)
            self._shading_status = QLabel()
            self._shading_status.setPixmap(self._error_pixmap)
            shading_lbl = QLabel(' SHADING')
            self._shading_text = QLabel('')
            shading_layout.addWidget(self._shading_status)
            shading_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            shading_layout.addWidget(shading_lbl)
            shading_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            shading_layout.addWidget(self._shading_text)

        if self._has_textures:
            textures_layout = QHBoxLayout()
            textures_layout.setContentsMargins(2, 2, 2, 2)
            textures_layout.setSpacing(2)
            textures_layout.setAlignment(Qt.AlignLeft)
            self._main_layout.addLayout(textures_layout)
            self._textures_status = QLabel()
            self._textures_status.setPixmap(self._error_pixmap)
            textures_lbl = QLabel('TEXTURES')
            self._textures_text = QLabel('')
            textures_layout.addWidget(self._textures_status)
            textures_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            textures_layout.addWidget(textures_lbl)
            textures_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
            textures_layout.addWidget(self._textures_text)
