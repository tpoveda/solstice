#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that defines a base class to load resources
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import base64

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtGui import *


def image_to_base64(image_path, image_format='PNG'):
    if os.path.isfile(image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read())


def base64_to_image(base64_string, image_format='PNG'):
    if isinstance(base64_string, basestring):
        ba = QByteArray.fromBase64(base64_string)
        image = QImage.fromData(ba, image_format)
        return image


def base64_to_bitmap(base64_string, bitmap_format='PNG'):
    if isinstance(base64_string, basestring):
        image = base64_to_image(base64_string, bitmap_format)
        if image != None:
            bitmap = QBitmap.fromImage(image)
            return bitmap


def base64_to_icon(base64_string, icon_format='PNG'):
    if isinstance(base64_string, basestring):
        bitmap = base64_to_bitmap (base64_string, icon_format)
        if bitmap != None:
            icon = QIcon(bitmap)
            return icon
