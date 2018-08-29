#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_group.py
# by Tomas Poveda
# Module that contains widgets to create groups
# ______________________________________________________________________
# ==================================================================="""


from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *


class SolsticeGroup(QGroupBox, object):
    def __init__(self, title):
        super(SolsticeGroup, self).__init__()

        self._collapsable = True
        self.setTitle(title)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self._widget = QWidget()
        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(10, 10, 10, 10)
        widget_layout.setSpacing(2)
        widget_layout.setAlignment(Qt.AlignCenter)
        self._widget.setLayout(widget_layout)
        main_layout.addWidget(self._widget)

        self.main_layout = widget_layout

        self.custom_ui()
        self.setup_signals()

    def mousePressEvent(self, event):
        super(SolsticeGroup, self).mousePressEvent(event)

        if not event.button() == Qt.LeftButton:
            return

        if self._collapsable:
            if event.y() < 30:
                self._widget.setVisible(not self._widget.isVisible())

    def custom_ui(self):
        pass

    def setup_signals(self):
        pass

    def collapse_group(self):
        self._widget.setVisible(False)

    def expand_group(self):
        self.setFixedSize((1 << 24) - 1)
        self.setVisible(True)

    def set_title(self, title):
        self.setTitle(title)

    def set_collapsable(self, flag):
        self._collapsable = flag
    # endregion
