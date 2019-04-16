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

import solstice.pipeline as sp
from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.widgets import exporteritem


class AnimationAssetItem(exporteritem.AbstractExporterItemWidget, object):

    clicked = Signal(QObject, QEvent)
    contextRequested = Signal(QObject, QAction)

    def __init__(self, asset, alembic_node, parent=None):

        self.abc_node = alembic_node
        self.abc_attrs = dict()

        super(AnimationAssetItem, self).__init__(asset, parent)

        self._update_attrs()

    def custom_ui(self):
        super(AnimationAssetItem, self).custom_ui()

        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')

        self.asset_lbl = QLabel(self.asset.name)
        self.item_layout.addWidget(self.asset_lbl, 0, 1, 1, 1)

        self.item_layout.setColumnStretch(1, 5)
        self.item_layout.setAlignment(Qt.AlignLeft)

    def _update_attrs(self):
        if self.attrs:
            return

        # Store transform attributes
        xform_attrs = sp.dcc.list_attributes(self.asset.name)
        for attr in xform_attrs:
            if attr not in defines.MUST_ATTRS:
                continue
            self.attrs[attr] = True

        # Store Alembic Node attrs
        abc_attrs = sp.dcc.list_attributes(self.abc_node)
        for attr in abc_attrs:
            if attr not in defines.ABC_ATTRS:
                continue
            self.abc_attrs[attr] = True
