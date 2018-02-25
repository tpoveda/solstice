#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pickers.py
# by Tomas Poveda
# Tool that allows to select the picker you want to open
# ______________________________________________________________________# ______________________________________________________________________
# ==================================================================="""

import os
import sys
from functools import partial

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import maya.cmds as cmds

from solstice_utils import _getMayaWindow, readJSON

class solstice_pickers(QMainWindow, object):
    def __init__(self):
        super(solstice_pickers, self).__init__(_getMayaWindow())

        win_name = 'solstice_pickers_window'

        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window(win_name, exists=True):
            cmds.deleteUI(win_name, window=True)
        elif cmds.windowPref(win_name, exists=True):
            cmds.windowPref(win_name, remove=True)

            # Set the dialog object name, window title and size
        self.setObjectName(win_name)
        self.setWindowTitle('Solstice Pickers - v.1.0')
        self.customUI()
        self.show()

    def customUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        main_layout.setAlignment(Qt.AlignCenter)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(2)
        main_layout.addLayout(buttons_layout)

        icons_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'icons')

        character_buttons = dict()
        character_school_anim_buttons = dict()
        for character_name in ['summer', 'winter', 'spring']:
            character_layout = QVBoxLayout()
            character_layout.setContentsMargins(2,2,2,2)
            character_layout.setSpacing(2)
            buttons_layout.addLayout(character_layout)
            character_label = QLabel(character_name.capitalize())
            character_label.setAlignment(Qt.AlignCenter)
            character_btn = QPushButton()
            character_btn.setIconSize(QSize(150, 150))
            character_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            character_btn.clicked.connect(partial(self.open_picker, character_name))
            character_icon_file = os.path.join(icons_path, '{0}_icon.png'.format(character_name))
            if os.path.isfile(character_icon_file):
                character_icon = QIcon(character_icon_file)
                character_btn.setIcon(character_icon)

            character_layout.addWidget(character_label)
            character_layout.addWidget(character_btn)

        character_school_anim_btn = QPushButton()
        character_school_anim_btn.setIconSize(QSize(150, 30))
        character_school_anim_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        character_school_anim_btn.clicked.connect(self.open_anim_picker)
        character_school_anim_file = os.path.join(icons_path, 'AnimSchoolLogoIcon.png')
        if os.path.isfile(character_school_anim_file):
            anim_school_icon = QIcon(character_school_anim_file)
            character_school_anim_btn.setIcon(anim_school_icon)
        main_layout.addWidget(character_school_anim_btn)

    def open_picker(self, character_name):

        command = 'from pickers import {0}Picker;reload({0}Picker);{0}Picker.solstice_{0}Picker.initPicker(fullWindow=False)'.format(character_name)
        try:
            exec(command)
        except Exception as e:
            print(str(e))
            QMessageBox.information(self, "{0} Picker".format(character_name.capitalize()), '{0} Picker is not created yet, wait for future updates!'.format(character_name.capitalize()))

    def open_anim_picker(self):

        anim_school_picker = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'externals'), 'animschool_picker')
        if sys.platform == 'win' or sys.platform == 'win32':
            anim_school_picker = os.path.join(anim_school_picker, 'win')
        else:
            anim_school_picker = os.path.join(anim_school_picker, 'mac')
        anim_school_picker_plugin_name = 'AnimSchoolPicker.mll'
        anim_school_picker_plugin = os.path.join(anim_school_picker, anim_school_picker_plugin_name)
        if not os.path.isfile(anim_school_picker_plugin):
            print(anim_school_picker_plugin)
            return
        if cmds.pluginInfo(anim_school_picker_plugin, query=True, loaded=True):
            pass
        else:
            cmds.loadPlugin(anim_school_picker_plugin, quiet=True)
        cmds.AnimSchoolPicker()






def initUI():
    solstice_pickers()