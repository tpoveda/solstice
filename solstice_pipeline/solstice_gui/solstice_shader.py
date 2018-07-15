#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_asset.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Shader in the Solstice Shader Library
# ______________________________________________________________________
# ==================================================================="""

import os

from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *


class ShaderWidget(QPushButton, object):
    def __init__(self, shader_name, swatch_dir, shader_path, parent=None):
        super(ShaderWidget, self).__init__(parent=parent)

        image = os.path.join(swatch_dir, shader_name).replace('\\', '/')
        self._button_icon = QIcon(QPixmap(image))
        self.setText(shader_name)
        self.setStyleSheet('background-image: url(' + image + '); background-repeat: no-repeat; background-position: center center; text-align: bottom; font-weight: bold;')
        self.setMinimumWidth(150)
        self.setMinimumHeight(150)
        self.setMaximumWidth(150)
        self.setMaximumHeight(150)
        self._item = os.path.join(shader_path, shader_name + '.sshader')