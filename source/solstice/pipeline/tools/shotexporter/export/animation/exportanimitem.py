#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base definition for export item widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.tools.shotexporter.core import defines, assetitem


class AnimationAssetItem(assetitem.ExporterAssetItem, object):

    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, asset, alembic_node, parent=None):
        self.abc_node = alembic_node
        self.abc_attrs = dict()
        super(AnimationAssetItem, self).__init__(asset, parent)

    def _update_attrs(self):
        if self._attrs:
            return

        super(AnimationAssetItem, self)._update_attrs()

        # Store Alembic Node attrs
        abc_attrs = sys.solstice.dcc.list_attributes(self.abc_node)
        for attr in abc_attrs:
            if attr not in defines.ABC_ATTRS:
                continue
            self.abc_attrs[attr] = True
