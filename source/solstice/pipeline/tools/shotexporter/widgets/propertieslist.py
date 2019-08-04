#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base definition for property list widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

from Qt.QtWidgets import *
from Qt.QtCore import *

from solstice.pipeline.gui import attributes


class BasePropertiesListWidget(QWidget, object):
    def __init__(self, parent=None):
        super(BasePropertiesListWidget, self).__init__(parent=parent)

        self._current_asset = None
        self.widgets = list()

        self.setMouseTracking(True)

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.grid_layout)

        scroll_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('QScrollArea { background-color: rgb(57,57,57);}')
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(scroll_widget)

        self.props_layout = QVBoxLayout()
        self.props_layout.setContentsMargins(1, 1, 1, 1)
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()
        scroll_widget.setLayout(self.props_layout)
        self.grid_layout.addWidget(scroll_area, 1, 0, 1, 4)

    def setup_signals(self):
        pass

    def all_attributes(self):
        all_attrs = list()
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget() is not None:
                all_attrs.append(child.widget())

        return all_attrs

    def add_attribute(self, attr_name):
        if not self._current_asset:
            return

        new_attr = attributes.BaseAttributeWidget(node=self._current_asset, attr_name=attr_name)
        new_attr.toggled.connect(self._on_update_attribute)
        self.widgets.append(new_attr)
        self.props_layout.insertWidget(0, new_attr)

        return new_attr

    def update_attributes(self, asset_widget):
        if asset_widget.asset == self._current_asset:
            return

        self.clear_properties()
        self._current_asset = asset_widget.asset

        xform_attrs = sys.solstice.dcc.list_attributes(asset_widget.asset.name)
        for attr in xform_attrs:
            new_attr = self.add_attribute(attr)
            if self._current_asset.attrs[new_attr.name] is True:
                new_attr.check()
            else:
                new_attr.uncheck()

    def clear_properties(self):
        del self.widgets[:]
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
        self.props_layout.setSpacing(0)
        self.props_layout.addStretch()

    def _on_update_attribute(self, attr_name, flag):
        if not self._current_asset:
            return

        if attr_name not in self._current_asset.attrs.keys():
            sys.solstice.logger.warning('Impossible to udpate attribute {} because node {} has no that attribute!'.format(attr_name, self._current_asset.asset))
            return

        self._current_asset.attrs[attr_name] = flag
