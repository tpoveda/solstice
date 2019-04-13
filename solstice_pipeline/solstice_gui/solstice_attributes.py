#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_attributes.py
# by Tomas Poveda
# Widgets to handle attributes
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *


class BaseAttributeWidget(QWidget, object):

    toggled = Signal(str, bool)

    def __init__(self, node, attr_name, parent=None):
        super(BaseAttributeWidget, self).__init__(parent=parent)

        self._node = node
        self._attribute_name = attr_name

        self.custom_ui()
        self.setup_signals()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.item_widget = QFrame()
        self.item_widget.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.item_widget.setStyleSheet('QFrame { background-color: rgb(55,55,55);}')
        self.item_layout = QGridLayout()
        # self.item_layout.setColumnStretch(1, 3)
        self.item_layout.setAlignment(Qt.AlignLeft)
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_widget.setLayout(self.item_layout)
        self.main_layout.addWidget(self.item_widget)

        self.attr_cbx = QCheckBox()
        self.attr_cbx.setChecked(True)
        self.item_layout.addWidget(self.attr_cbx, 0, 1)

        self.attr_lbl = QLabel()
        self.attr_lbl.setText(str(self._attribute_name))
        self.item_layout.addWidget(self.attr_lbl, 0, 2)

        self.setMinimumHeight(25)

    def setup_signals(self):
        self.attr_cbx.toggled.connect(self._on_toggle_cbx)

    @property
    def name(self):
        return self._attribute_name

    @property
    def node(self):
        return self._node

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

    def _on_toggle_cbx(self, flag):
        self.toggled.emit(self.name, flag)
