#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class for exporter widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.externals.solstice_qt.QtWidgets import *
from solstice.pipeline.externals.solstice_qt.QtCore import *

import solstice.pipeline as sp
from solstice.pipeline.gui import base, splitters


class BaseExporter(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(BaseExporter, self).__init__(parent=parent)

        self.export_list.init_ui()

    def custom_ui(self):
        super(BaseExporter, self).custom_ui()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        self.export_list = self.get_exporter_list_widget()
        self.properties_widget = self.get_exporter_properties_widget()
        main_splitter.addWidget(self.export_list)
        main_splitter.addWidget(self.properties_widget)

        self.save_btn = QPushButton(str(self.get_export_button_text()))
        self.save_btn.setMinimumHeight(30)
        self.save_btn.setMinimumWidth(80)
        save_layout = QHBoxLayout()
        save_layout.setContentsMargins(0, 0, 0, 0)
        save_layout.setSpacing(0)
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        save_layout.addWidget(self.save_btn)
        save_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addLayout(save_layout)

    def setup_signals(self):
        self.export_list.itemClicked.connect(self._on_update_properties)
        self.save_btn.clicked.connect(self._on_save)

    def get_exporter_list_widget(self):
        """
        Returns exporter list widget used by the exporter
        Override in child classes
        :return: exporter.BaseExporter
        """

        raise NotImplementedError('You must implement get_exporter_list_widget() in child classes')

    def get_exporter_properties_widget(self):
        """
        Returns exporter properties widget used by the exporter
        Override in child classes
        :return: exporter.BasePropertiesList
        """

        raise NotImplementedError('You must implement get_exporter_properties_widget() in child classes')

    def get_export_button_text(self):
        """
        Returns exporter button text
        :return: str
        """

        return 'SAVE'

    def refresh(self):
        self.export_list.refresh_exporter()

    def _on_update_properties(self, asset_widget):
        if not asset_widget:
            return
        asset_widget = asset_widget[0]

        if asset_widget and sp.dcc.object_exists(asset_widget.asset.name):
            self.properties_widget.update_attributes(asset_widget)
        else:
            sp.logger.warning('Impossible to update properties because object {} does not exists!'.format(asset_widget.asset))
            self.properties_widget.clear_properties()

    def _on_clear_properties(self):
        self.properties_widget.clear_properties()

    def _on_save(self):
        pass
