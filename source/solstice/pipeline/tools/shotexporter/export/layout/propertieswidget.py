#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definition for animation property list widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.tools.shotexporter.widgets import propertieslist

reload(propertieslist)


class LayoutPropertiesWidget(propertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(LayoutPropertiesWidget, self).__init__(parent=parent)
