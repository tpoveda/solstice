#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to select the picker you want to open
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import traceback
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import window
from solstice.pipeline.utils import pythonutils
from solstice.pipeline.tools.pickers.picker import utils as utils
from solstice.pipeline.resources import resource

if sp.is_maya():
    import maya.cmds as cmds


class SolsticePickers(window.Window, object):

    name = 'Solstice_Pickers'
    title = 'Solstice Tools - Picker Tool'
    version = '1.2'

    def __init__(self):
        super(SolsticePickers, self).__init__()

    def custom_ui(self):
        super(SolsticePickers, self).custom_ui()

        self.set_logo('solstice_pickers_logo')
        self.set_info_url('https://tpoveda.github.io/solstice/solsticepipeline/solsticetools/solsticepickers/')

        self.resize(300, 200)

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
            character_icon = resource.icon(name='{}_icon'.format(character_name), extension='png')
            character_btn.setIcon(character_icon)
            character_layout.addWidget(character_lbl)
            character_layout.addWidget(character_btn)

        # self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # anim_school_layout = QHBoxLayout()
        # anim_school_layout.setAlignment(Qt.AlignLeft)
        # self.main_layout.addLayout(anim_school_layout)
        # main_warning_layout = QVBoxLayout()
        # warning_layout = QHBoxLayout()
        # folder_warning_layout = QHBoxLayout()
        # warning_layout.setContentsMargins(2, 2, 2, 2)
        # warning_layout.setSpacing(2)
        # folder_warning_layout.setContentsMargins(2, 2, 2, 2)
        # folder_warning_layout.setSpacing(2)
        # main_warning_layout.addLayout(warning_layout)
        # main_warning_layout.addLayout(solstice_splitters.SplitterLayout())
        # main_warning_layout.addLayout(folder_warning_layout)
        # warning_lbl = QLabel()
        # warning_lbl.setPixmap(solstice_resource.pixmap('warning', category='icons'))
        # warning_info = QLabel('If you have problems opening Solstice Pickers, please contact Solstice TD team.\nMeanwhile, you can use Solstice Anim School Pickers.')
        # warning_layout.addWidget(warning_lbl)
        # warning_layout.addWidget(warning_info)
        # self.pickers_path_lbl = QLabel()
        # open_pickers_path_btn = QPushButton()
        # open_pickers_path_btn.setIcon(solstice_resource.icon('folder'))
        # folder_warning_layout.addWidget(self.pickers_path_lbl)
        # folder_warning_layout.addWidget(open_pickers_path_btn)
        # anim_school_btn = QPushButton()
        # anim_school_btn.setIconSize(QSize(50, 50))
        # anim_school_btn.setIcon(solstice_resource.icon('anim_school_logo'))
        # anim_school_btn.setMinimumSize(QSize(45, 45))
        # documentation_btn = QPushButton()
        # documentation_btn.setIconSize(QSize(50, 50))
        # documentation_btn.setIcon(solstice_resource.icon('documentation'))
        # documentation_btn.setMinimumSize(QSize(45, 45))
        # anim_school_layout.addLayout(main_warning_layout)
        # anim_school_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
        # anim_school_layout.addWidget(anim_school_btn)
        # anim_school_layout.addWidget(solstice_splitters.get_horizontal_separator_widget())
        # anim_school_layout.addWidget(documentation_btn)
        # anim_school_btn.clicked.connect(self.open_anim_school_picker)

        self._update_pickers_label()
        # open_pickers_path_btn.clicked.connect(self._open_pickers_folder)
        # documentation_btn.clicked.connect(self._open_pickers_documentation)

    def open_picker(self, character_name):
        command = 'from solstice.pipeline.tools.pickers.{0} import picker;reload(picker);picker.run(full_window=False);'.format(character_name)
        try:
            exec(command)
        except Exception as e:
            sys.solstice.logger.error('{} | {}'.format(e, traceback.format_exc()))
            QMessageBox.information(self, '{} Picker'.format(character_name.capitalize()), '{} Picker is not created yet, wait for future updates!'.format(character_name.capitalize()))

    def open_anim_school_picker(self):
        sys.solstice.logger.debug('Opening Anim School Picker')
        externals_path = sp.get_externals_path()
        if not os.path.exists(externals_path):
            sys.solstice.logger.error('Externals Path {} does not exists! Please contact TD team!'.format(externals_path))
            return
        anim_school_folder = os.path.join(externals_path, 'solstice_animschoolpicker')
        if not os.path.exists(anim_school_folder):
            sys.solstice.logger.error('Anim School Picker Folder {} does not exists! Please contact TD team!'.format(anim_school_folder))
            return

        if sys.platform == 'win32':
            anim_school_plugin = os.path.join(anim_school_folder, 'win', 'AnimSchoolPicker.mll')
        elif sys.platform == 'darwin':
            anim_school_plugin = os.path.join(anim_school_folder, 'mac', 'AnimSchoolPicker.bundle')
        else:
            print('Solstice Tools are not compatible with your OS {}'.format(sys.platform))
            return

        if not os.path.exists(anim_school_plugin):
            sys.solstice.logger.error('No valid Anim School Picker Plugin file found: {}'.format(anim_school_plugin))
            return

        if cmds.pluginInfo('AnimSchoolPicker', query=True, loaded=True):
            sys.solstice.logger.debug('Anim School Picker already loaded')
        else:
            try:
                cmds.loadPlugin(anim_school_plugin)
                sys.solstice.logger.debug('Anim School Picker Plugin loaded successfully!')
            except Exception as e:
                sys.solstice.logger.error('Error while loading Anim School Picker Plugin. Please contact TD team!')
                sys.solstice.logger.error(str(e))
                return

        try:
            cmds.AnimSchoolPicker()
            sys.solstice.logger.debug('Anim School Picker launched successfully!')
        except Exception as e:
            sys.solstice.logger.error('Error while launcher Anim School Picker. Please contact TD team!')
            sys.solstice.logger.error(str(e))
            return

        sys.solstice.logger.debug('Trying to open Solstice Pickers MEL scripts ...')
        try:
            self._init_picker_scripts()
            sys.solstice.logger.debug('Solstice Picker Scripts loaded successfully!')
        except Exception as e:
            sys.solstice.logger.warning('Solstice Picker Scripts have not been loaded successfully! Picker Scripts will not work!')
            pass

    def _update_pickers_label(self):
        sys.solstice.logger.debug('Updating Pickers Path label ...')
        externals_path = sp.get_externals_path()
        if not os.path.exists(externals_path):
            sys.solstice.logger.error('Externals Path {} does not exists! Please contact TD team!'.format(externals_path))
            return
        anim_school_folder = os.path.join(externals_path, 'solstice_animschoolpicker')
        if not os.path.exists(anim_school_folder):
            sys.solstice.logger.error(
                'Anim School Picker Folder {} does not exists! Please contact TD team!'.format(anim_school_folder))
            return
        anim_school_pickers_folder = os.path.join(anim_school_folder, 'pickers')
        if not os.path.exists(anim_school_pickers_folder):
            sys.solstice.logger.warning('Solstice Pickers for Anim School Picker not found!')
        else:
            pass
            # self.pickers_path_lbl.setText('Pickers Path: {}'.format(anim_school_pickers_folder))

    def _open_pickers_folder(self):
        sys.solstice.logger.debug('Opening Pickers Folder')
        externals_path = sp.get_externals_path()
        if not os.path.exists(externals_path):
            sys.solstice.logger.error('Externals Path {} does not exists! Please contact TD team!'.format(externals_path))
            return
        anim_school_folder = os.path.join(externals_path, 'solstice_animschoolpicker')
        if not os.path.exists(anim_school_folder):
            sys.solstice.logger.error(
                'Anim School Picker Folder {} does not exists! Please contact TD team!'.format(anim_school_folder))
            return
        anim_school_pickers_folder = os.path.join(anim_school_folder, 'pickers')
        if not os.path.exists(anim_school_pickers_folder):
            sys.solstice.logger.warning('Solstice Pickers for Anim School Picker not found!')
        else:
            pythonutils.open_file(anim_school_pickers_folder)

    def _open_pickers_documentation(self):
        pickers_documentation_url = 'https://tpoveda.github.io/solstice/solsticepipeline/solsticetools/solsticepickers/'
        pythonutils.open_web(pickers_documentation_url)

    def _open_studio_library(self):
        try:
            sys.solstice.logger.debug('Trying to import Studio Libary ...')
            import solstice_studiolibrarymaya
            solstice_studiolibrarymaya.registerItems()
            solstice_studiolibrarymaya.enableMayaClosedEvent()
            import solstice_studiolibrarymaya.mayalibrarywidget
            import solstice_studiolibrary.librarywidget
            sys.solstice.logger.debug('Studio Library imported successfully!')
            sys.solstice.logger.debug('Trying to open Studio Library ...')
            try:
                self.pose_widget = solstice_studiolibrary.librarywidget.LibraryWidget.instance()
            except Exception:
                try:
                    reload(solstice_studiolibrary.librarywidget)
                    self.pose_widget = solstice_studiolibrary.librarywidget.LibraryWidget.instance()
                except Exception as e:
                    sys.solstice.logger.error('Error while opening Studio Libary. Please contact TD team!')
                    sys.solstice.logger.error(str(e))
            sys.solstice.logger.debug('Studio Library opened successfully!')
        except Exception as e:
            sys.solstice.logger.error('Error while opening Studio Libary. Please contact TD team!')
            sys.solstice.logger.error(str(e))
            return

    def _init_picker_scripts(self):
        if not os.path.exists(utils.scripts_path):
            cmds.error('Solstice Picker Scripts not found!')

        sys.solstice.logger.debug('Loading pickers MEL scripts ...')

        utils.load_script('vlRigIt_getModuleFromControl.mel')
        utils.load_script('vlRigIt_getControlsFromModuleList.mel')
        utils.load_script('vlRigIt_selectModuleControls.mel')
        utils.load_script('vlRigIt_snap_ikFk.mel')
        utils.load_script('vl_resetTransformations.mel')
        utils.load_script('vl_resetAttributes.mel')
        utils.load_script('vl_contextualMenuBuilder.mel')

def run():
    SolsticePickers().show()
