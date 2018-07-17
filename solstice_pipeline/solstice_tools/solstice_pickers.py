#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_scatter.py
# by Tomas Poveda
# Tool that allows to select the picker you want to open
# ______________________________________________________________________
# ==================================================================="""

from functools import partial

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from solstice_gui import solstice_windows
from resources import solstice_resource


class SolsticePickers(solstice_windows.Window, object):

    name = 'Solstice_Pickers'
    title = 'Solstice Tools - Picker Tool'
    version = '1.0'
    docked = False

    def __init__(self, name='PickersWindow', parent=None, **kwargs):
        super(SolsticePickers, self).__init__(name=name, parent=parent)

    def custom_ui(self):
        super(SolsticePickers, self).custom_ui()

        self.set_logo('solstice_pickers_logo')

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(2)
        self.main_layout.addLayout(buttons_layout)

        for character_name in ['summer', 'winter', 'spring']:
            character_layout = QVBoxLayout()
            character_layout.setContentsMargins(2, 2, 2, 2)
            character_layout.setSpacing(2)
            buttons_layout.addLayout(character_layout)
            character_lbl = QLabel(character_name.capitalize())
            character_lbl.setAlignment(Qt.AlignCenter)
            character_btn = QPushButton()
            character_btn.setIconSize(QSize(150, 150))
            character_btn.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            character_btn.clicked.connect(partial(self.open_picker, character_name))
            character_icon = solstice_resource.icon(name='{}_icon'.format(character_name), extension='png')
            character_btn.setIcon(character_icon)
            character_layout.addWidget(character_lbl)
            character_layout.addWidget(character_btn)

    def open_picker(self, character_name):
        command = 'from solstice_pipeline.solstice_pickers.{0} import picker;reload(picker);picker.run(full_window=False);'.format(character_name)
        try:
            exec(command)
        except Exception as e:
            print(str(e))
            QMessageBox.information(self, '{} Picker'.format(character_name.capitalize()), '{} Picker is not created yet, wait for future updates!'.format(character_name.capitalize()))


def run():
    SolsticePickers.run()
