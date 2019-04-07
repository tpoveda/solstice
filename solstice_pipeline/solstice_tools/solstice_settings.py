#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Module that contains classes to manage preferences
# ==================================================================="""

import os
import json
import logging

import maya.app.general.mayaMixin as mayaMixin

from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtCore import *

import solstice_pipeline as sp


class SolsticeSettings(QObject, object):
    """
    Class that manages global Solstice Tools Preferences
    """

    default_preferences = {
        'INITIAL STARTUP': True,
        'LOG_LEVEL': logging.WARN,
        'AUTOMATIC_REPORT': False,
        'REPORT': True,
        'SENDER': ' '
    }

    def __init__(self):
        self.ui = SolsticeSettingsTool()
        self.ui.prefsSaved.connect(self.dump_prefs)
        self.solstice_globals = self.parse_prefs()
        self.update_ui()

    def __getitem__(self, attr):
        return self.solstice_globals[attr]

    def __setitem__(self, attr, value):
        if attr in self.solstice_globals.keys():
            if type(value) is type(self.solstice_globals[attr]):
                sp.logger.debug('Set prefs: {}={}'.format(attr, value))
                self.solstice_globals[attr] = value
                self.dump_prefs
            else:
                raise TypeError('{} must be of type {}'.format(attr, type(self.solstice_globals[attr])))
        else:
            raise KeyError('{} is not a valid option'.format(attr))

    def __iter__(self):
        for attr, value in self.solstice_globals.items():
            yield attr, value

    def update_ui(self):
        """
        Fill settings UI with existing globals
        """

        for key, value in self:
            self.ui.add_preference_widget(key, value)

    def parse_prefs(self):
        """
        Parses solstice global preferences in Solstice Tools Preferences Folder
        """

        pref_file = os.path.join(os.environ['SOLSTICE_PREFS_DIR'], 'solstice_prefs.json')
        if not os.path.isfile(pref_file):
            with open(pref_file, 'w') as f:
                json.dump(self.default_preferences, f)

        solstice_globals = dict()
        with open(pref_file, 'r') as f:
            try:
                solstice_globals = json.load(f)
            except ValueError:
                raise RuntimeError('Could not load preferences file from: {}\n Maybe is not properly formatted. Try to delete it ...'.format(pref_file))

        return solstice_globals

    def dump_prefs(self, prefs=None):
        """
        Dumps the current settings to file
        :return:
        """

        pref_file = os.path.join(os.environ['SOLSTICE_PREFS_DIR'], 'solstice_prefs.json')
        with open(pref_file, 'w') as f:
            if prefs:
                self.solstice_globals = prefs

            json.dump(self.solstice_globals, f)
            sp.logger.debug('Solstice globals dumped: {}'.format(self.solstice_globals))
        sp.logger.set_log_level(self.solstice_globals['LOG_LEVEL'])

    def show(self):
        self.ui.show(dockable=True)


class SolsticeSettingsTool(mayaMixin.MayaQWidgetDockableMixin, QWidget):

    prefsSaved = Signal(dict)

    def __init__(self, parent=None):
        super(SolsticeSettingsTool, self).__init__(parent=parent)

        self.setWindowTitle('Solstice Tools - Settings')
        self.setGeometry(250, 250, 400, 150)

        self.custom_ui()
        self.setup_signals()

        self.preferences_tracking_dir = dict()

    def custom_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addStretch()
        self.save_btn = QPushButton('Save')
        self.main_layout.addWidget(self.save_btn)

    def setup_signals(self):
        self.save_btn.clicked.connect(self._on_save)

    def add_preference_widget(self, name, value):
        if isinstance(value, bool):
            widget = BoolWidget(name, value)
            self.main_layout.insertWidget(0, widget)
            self.preferences_tracking_dir[widget.name_lbl] = widget.bool_cbx
        elif isinstance(value, str) or isinstance(value, unicode):
            widget = StringWidget(name, value)
            self.main_layout.insertWidget(0, widget)
            self.preferences_tracking_dir[widget.name_lbl] = widget.line_edt
        elif isinstance(value, int):
            widget = IntegerWidget(name, value)
            self.main_layout.insertWidget(0, widget)
            self.preferences_tracking_dir[widget.name_lbl] = widget.int_spn
        elif isinstance(value, float):
            widget = FloatWidget(name, value)
            self.main_layout.insertWidget(0, widget)
            self.preferences_tracking_dir[widget.name_lbl] = widget.float_spn
        else:
            sp.logger.debug('No assignment for {} : {} : {}'.format(name, value, type(value)))

    def _on_save(self):
        prefs = dict()
        for attr_lbl, value_widget in self.preferences_tracking_dir.items():
            attr = attr_lbl.text()
            if isinstance(value_widget, QCheckBox):
                value = value_widget.isChecked()
            elif isinstance(value_widget, QLineEdit):
                value = value_widget.text()
            elif isinstance(value_widget, QSpinBox) or isinstance(value_widget, QDoubleSpinBox):
                value = value_widget.value()
            else:
                raise RuntimeError('Not valid widget to read preference from')

            prefs[attr] = value

        self.prefsSaved.emit(prefs)
        self.close()


class BoolWidget(QWidget):
    def __init__(self, name, value):
        super(BoolWidget, self).__init__()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        main_layout.addWidget(self.name_lbl)

        self.bool_cbx = QCheckBox()
        self.bool_cbx.setChecked(value)
        main_layout.addWidget(self.bool_cbx)


class StringWidget(QWidget):
    def __init__(self, name, value):
        super(StringWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        main_Layout = QHBoxLayout()
        main_Layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_Layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        main_Layout.addWidget(self.name_lbl)

        self.line_edt = QLineEdit()
        self.line_edt.setText(value)
        main_Layout.addWidget(self.line_edt)


class IntegerWidget(QWidget):
    def __init__(self, name, value):
        super(IntegerWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        main_layout.addWidget(self.name_lbl)

        self.int_spn = QSpinBox()
        self.int_spn.setValue(value)
        main_layout.addWidget(self.int_spn)


class FloatWidget(QWidget):
    def __init__(self, name, value):
        super(FloatWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.name_lbl = QLabel(name)
        self.name_lbl.setFixedWidth(150)
        main_layout.addWidget(self.name_lbl)

        self.float_spn = QDoubleSpinBox()
        self.float_spn.setValue(value)
        main_layout.addWidget(self.float_spn)
