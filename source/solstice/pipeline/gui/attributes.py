#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widgets to handle attributes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from Qt.QtWidgets import *
from Qt.QtCore import *

from solstice.pipeline.gui import splitters


class BaseAttributeWidget(QWidget, object):

    toggled = Signal(str, bool)

    def __init__(self, node, attr_name, attr_value=None, parent=None):
        super(BaseAttributeWidget, self).__init__(parent=parent)

        self._node = node

        self.custom_ui()
        self.setup_signals()

        self.attr_lbl.setText(attr_name)
        if attr_value:
            self.set_value(attr_value)

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.item_widget = QFrame()
        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')
        self.item_layout = QHBoxLayout()
        # self.item_layout.setColumnStretch(1, 3)
        self.item_layout.setAlignment(Qt.AlignLeft)
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_widget.setLayout(self.item_layout)
        self.main_layout.addWidget(self.item_widget)

        self.attr_cbx = QCheckBox()
        self.attr_cbx.setChecked(True)
        self.item_layout.addWidget(self.attr_cbx)

        self.attr_lbl = QLabel()
        self.item_layout.addWidget(self.attr_lbl)

        self.attr_widget = self.attribute_widget()
        if self.attr_widget:
            self.attr_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.item_layout.addWidget(splitters.get_horizontal_separator_widget())
            self.item_layout.addWidget(self.attr_widget)

        self.setMinimumHeight(25)

    def setup_signals(self):
        self.attr_cbx.toggled.connect(self._on_toggle_cbx)

    @property
    def name(self):
        return self.attr_lbl.text()

    @property
    def node(self):
        return self._node

    def attribute_widget(self):
        return None

    def set_value(self, value):
        pass

    def hide_check(self):
        self.attr_cbx.hide()

    def check(self):
        self.attr_cbx.blockSignals(True)
        self.attr_cbx.setChecked(True)
        self.attr_cbx.blockSignals(False)

    def uncheck(self):
        self.attr_cbx.blockSignals(True)
        self.attr_cbx.setChecked(False)
        self.attr_cbx.blockSignals(False)

    def toggle(self):
        self.attr_cbx.blockSignals(True)
        self.attr_cbx.setChecked(not self.attr_cbx.isChecked())
        self.attr_cbx.blockSignals(False)

    def lock(self):
        if self.attr_widget:
            self.attr_widget.setEnabled(False)

    def unlock(self):
        if self.attr_widget:
            self.attr_widget.setEnabled(True)

    def _on_toggle_cbx(self, flag):
        self.toggled.emit(self.name, flag)


class FloatAttribute(BaseAttributeWidget, object):
    def __init__(self, node, attr_name, attr_value=None, parent=None):
        super(FloatAttribute, self).__init__(node=node, attr_name=attr_name, attr_value=attr_value, parent=parent)

    def attribute_widget(self):
        w = QDoubleSpinBox()
        w.setDecimals(3)
        w.setLocale(QLocale.C)
        return w

    def set_value(self, value):
        self.attr_widget.setValue(value)


class StringAttribute(BaseAttributeWidget, object):
    def __init__(self, node, attr_name, attr_value=None, parent=None):
        super(StringAttribute, self).__init__(node=node, attr_name=attr_name, attr_value=attr_value, parent=parent)

    def attribute_widget(self):
        return QLineEdit()

    def set_value(self, value):
        self.attr_widget.setText(value)
