#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to smooth the workflow between Maya and Artella
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import time
from functools import partial
from distutils.util import strtobool

from solstice.pipeline.externals import treelib

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.core import asset as base_asset, assetviewer
from solstice.pipeline.gui import window, stack, splitters, spinner
from solstice.pipeline.utils import pythonutils, artellautils, artellaclasses, qtutils
from solstice.pipeline.resources import resource

from solstice.pipeline.tools.pipelinizer import sequencer
from solstice.pipeline.tools.pipelinizer.widgets import user

if sp.is_maya():
    import maya.cmds as cmds


class PipelinizerSettings(QDialog, object):
    def __init__(self, parent):
        super(PipelinizerSettings, self).__init__(parent=parent)

        self.setObjectName('PipelinizerSettingsDialog')
        self.setWindowTitle('Pipelinizer - Settings')
        self.setMinimumWidth(250)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(2)
        frame.setLayout(frame_layout)
        main_layout.addWidget(frame)

        self._auto_check_published_cbx = QCheckBox('Auto Check Published Versions?')
        frame_layout.addWidget(self._auto_check_published_cbx)
        self._auto_check_working_cbx = QCheckBox('Auto Check Working Versions?')
        frame_layout.addWidget(self._auto_check_working_cbx)
        self._auto_check_lock_cbx = QCheckBox('Check Lock/Unlock Working Versions?')
        frame_layout.addWidget(self._auto_check_lock_cbx)

        main_layout.addLayout(splitters.SplitterLayout())

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(1)
        main_layout.addLayout(bottom_layout)

        save_btn = QPushButton('Save')
        cancel_btn = QPushButton('Cancel')
        bottom_layout.addWidget(save_btn)
        bottom_layout.addWidget(cancel_btn)

        # ===========================================================================

        self._settings = self.parent().settings
        if not self._settings:
            return

        if self._settings.has_option(self._settings.app_name, 'auto_check_published'):
            self._auto_check_published_cbx.setChecked(strtobool(self._settings.get('auto_check_published')))
        if self._settings.has_option(self._settings.app_name, 'auto_check_working'):
            self._auto_check_working_cbx.setChecked(strtobool(self._settings.get('auto_check_working')))
        if self._settings.has_option(self._settings.app_name, 'auto_check_lock'):
            self._auto_check_lock_cbx.setChecked(strtobool(self._settings.get('auto_check_lock')))

        # ===========================================================================

        save_btn.clicked.connect(self._save_settings)
        cancel_btn.clicked.connect(self.close)

        # ===========================================================================

        self.exec_()

    def _save_settings(self):
        self._update_settings()
        self.close()

    def _update_settings(self):
        if self._settings.has_option(self._settings.app_name, 'auto_check_published'):
            self._settings.set(self._settings.app_name, 'auto_check_published', str(self._auto_check_published_cbx.isChecked()))
        if self._settings.has_option(self._settings.app_name, 'auto_check_working'):
            self._settings.set(self._settings.app_name, 'auto_check_working', str(self._auto_check_working_cbx.isChecked()))
        if self._settings.has_option(self._settings.app_name, 'auto_check_lock'):
            self._settings.set(self._settings.app_name, 'auto_check_lock', str(self._auto_check_lock_cbx.isChecked()))
        self._settings.update()
        sys.solstice.logger.debug('{0}: Settings Updated successfully!'.format(self._settings.app_name))


class PipelinizerWaiting(QFrame, object):
    def __init__(self, parent=None):
        super(PipelinizerWaiting, self).__init__(parent)

        self.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.wait_spinner = spinner.WaitSpinner(spinner_type=spinner.SpinnerType.Loading)
        self.wait_spinner.bg.setFrameShape(QFrame.NoFrame)
        self.wait_spinner.bg.setFrameShadow(QFrame.Plain)

        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
        main_layout.addWidget(self.wait_spinner)
        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))


class Pipelinizer(window.Window, object):

    name = 'SolsticePipelinizer'
    title = 'Solstice Tools - Artella Pipeline'
    version = '1.8'

    def __init__(self):
        self._projects = None
        super(Pipelinizer, self).__init__()

    def _get_separator(self):
        v_div_w = QWidget()
        v_div_l = QVBoxLayout()
        v_div_l.setAlignment(Qt.AlignLeft)
        v_div_l.setContentsMargins(0, 0, 0, 0)
        v_div_l.setSpacing(0)
        v_div_w.setLayout(v_div_l)
        v_div = QFrame()
        v_div.setMinimumHeight(30)
        v_div.setFrameShape(QFrame.VLine)
        v_div.setFrameShadow(QFrame.Sunken)
        v_div_l.addWidget(v_div)
        return v_div_w

    def custom_ui(self):
        super(Pipelinizer, self).custom_ui()

        # Set Tool Logo
        self.set_logo('solstice_pipeline_logo')
        self.set_info_url('https://tpoveda.github.io/solstice/solsticepipeline/solsticetools/pipelinizer/tool/')

        self.resize(1100, 900)

        # Create Settings File
        if os.path.isfile(self.settings.config_file):
            if not self.settings.has_option(self.settings.app_name, 'auto_check_published'):
                self.settings.set(self.settings.app_name, 'auto_check_published', str(False))
            if not self.settings.has_option(self.settings.app_name, 'auto_check_working'):
                self.settings.set(self.settings.app_name, 'auto_check_working', str(False))
            if not self.settings.has_option(self.settings.app_name, 'auto_check_lock'):
                self.settings.set(self.settings.app_name, 'auto_check_lock', str(False))
            self.settings.update()

        # User Icon
        self.user_icon = user.UserWidget()
        self.user_icon.move(1030, 5)
        self._logo_scene.addWidget(self.user_icon)

        # Top Menu Bar
        top_menu_layout = QGridLayout()
        top_menu_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(top_menu_layout)
        artella_project_btn = QToolButton()
        artella_project_btn.setText('Artella')
        artella_project_btn.setIcon(resource.icon('artella'))
        artella_project_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        project_folder_btn = QToolButton()
        project_folder_btn.setText('Project')
        project_folder_btn.setIcon(resource.icon('folder'))
        project_folder_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        synchronize_btn = QToolButton()
        synchronize_btn.setText('Synchronize')
        synchronize_btn.setPopupMode(QToolButton.InstantPopup)
        synchronize_btn.setIcon(resource.icon('sync'))
        synchronize_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        settings_btn = QToolButton()
        settings_btn.setText('Settings')
        settings_btn.setIcon(resource.icon('settings'))
        settings_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        for i, btn in enumerate([self._get_separator(), artella_project_btn, self._get_separator(), project_folder_btn, self._get_separator(), synchronize_btn, self._get_separator(), settings_btn, self._get_separator()]):
            top_menu_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignCenter)

        synchronize_menu = QMenu(self)
        sync_characters_action = QAction('Characters', self)
        sync_props_action = QAction('Props', self)
        sync_background_elements_action = QAction('Background Elements', self)
        sync_all_action = QAction('All', self)
        for action in [sync_characters_action, sync_props_action, sync_background_elements_action, sync_all_action]:
            synchronize_menu.addAction(action)
        synchronize_menu.addSeparator()
        sync_sequences_action = QAction('Sequences', self)
        synchronize_menu.addAction(sync_sequences_action)
        synchronize_btn.setMenu(synchronize_menu)

        sync_characters_menu = QMenu(self)
        sync_characters_action.setMenu(sync_characters_menu)
        sync_characters_all_action = QAction('All', self)
        sync_character_model_action = QAction('Model', self)
        sync_character_textures_action = QAction('Textures', self)
        sync_character_shading_action = QAction('Shading', self)
        sync_character_grooming_action = QAction('Groom', self)
        sync_characters_menu.addAction(sync_characters_all_action)
        sync_characters_menu.addSeparator()
        for action in [sync_character_model_action, sync_character_textures_action, sync_character_shading_action, sync_character_grooming_action]:
            sync_characters_menu.addAction(action)

        sync_background_elements_menu = QMenu(self)
        sync_background_elements_action.setMenu(sync_background_elements_menu)
        sync_background_elements_all_action = QAction('All', self)
        sync_background_elements_model_action = QAction('Model', self)
        sync_background_elements_textures_action = QAction('Textures', self)
        sync_background_elements_shading_action = QAction('Shading', self)
        sync_background_elements_menu.addAction(sync_background_elements_all_action)
        sync_background_elements_menu.addSeparator()
        for action in [sync_background_elements_model_action, sync_background_elements_textures_action, sync_background_elements_shading_action]:
            sync_background_elements_menu.addAction(action)

        sync_props_menu = QMenu(self)
        sync_props_action.setMenu(sync_props_menu)
        sync_props_all_action = QAction('All', self)
        sync_props_model_action = QAction('Model', self)
        sync_props_textures_action = QAction('Textures', self)
        sync_props_shading_action = QAction('Shading', self)
        sync_props_menu.addAction(sync_props_all_action)
        sync_props_menu.addSeparator()
        for action in [sync_props_model_action, sync_props_textures_action, sync_props_shading_action]:
            sync_props_menu.addAction(action)

        self.stack = stack.SlidingStackedWidget(parent=self)
        self.main_layout.addWidget(self.stack)

        wait_widget = PipelinizerWaiting()
        self.stack.addWidget(wait_widget)

        # Pipelinizer Widgets
        self._tab_widget = QTabWidget()
        self._tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tab_widget.setMinimumHeight(330)
        self.stack.addWidget(self._tab_widget)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        categories_widget.setLayout(categories_layout)

        sequences_widget = QWidget()
        sequences_widget.setObjectName('SequencerWidget')
        sequences_layout = QVBoxLayout()
        sequences_layout.setContentsMargins(0, 0, 0, 0)
        sequences_layout.setSpacing(0)
        sequences_widget.setLayout(sequences_layout)

        self._tab_widget.addTab(categories_widget, 'Assets Manager')
        self._tab_widget.addTab(sequences_widget, 'Loading | Sequence Manager')
        self._tab_widget.setTabEnabled(1, False)

        # ================== Asset Manager Widget
        main_categories_menu_layout = QHBoxLayout()
        main_categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        main_categories_menu_layout.setSpacing(0)
        categories_layout.addLayout(main_categories_menu_layout)

        categories_menu = QWidget()
        categories_menu_layout = QVBoxLayout()
        categories_menu_layout.setContentsMargins(0, 0, 0, 0)
        categories_menu_layout.setSpacing(0)
        categories_menu_layout.setAlignment(Qt.AlignTop)
        categories_menu.setLayout(categories_menu_layout)
        main_categories_menu_layout.addWidget(categories_menu)

        asset_splitter = QSplitter(Qt.Horizontal)
        main_categories_menu_layout.addWidget(asset_splitter)

        self._asset_viewer = assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_pressed_callback=self.update_asset_info,
            parent=self)
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        asset_splitter.addWidget(self._asset_viewer)

        self._asset_viewer.first_empty_cell()

        self._info_asset_widget = QWidget()
        self._info_asset_widget.setVisible(False)
        info_asset_layout = QVBoxLayout()
        info_asset_layout.setContentsMargins(5, 5, 5, 5)
        info_asset_layout.setSpacing(5)
        self._info_asset_widget.setLayout(info_asset_layout)
        self._info_asset_widget.setMinimumWidth(200)
        asset_splitter.addWidget(self._info_asset_widget)

        self._categories_btn_group = QButtonGroup(self)
        self._categories_btn_group.setExclusive(True)
        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            new_btn = QPushButton(category)
            new_btn.toggled.connect(partial(self._change_category, category))
            categories_buttons[category] = new_btn
            categories_buttons[category].setCheckable(True)
            categories_menu_layout.addWidget(new_btn)
            self._categories_btn_group.addButton(new_btn)
        categories_buttons['All'].setChecked(True)

        # Sequence Manager Widget
        self.sequencer = sequencer.SolsticeSequencer()
        sequences_layout.addWidget(self.sequencer)

        # =================================================================================================

        self.sequencer.sequencerInitialized.connect(self._sequencer_loaded)
        artella_project_btn.clicked.connect(self.open_project_in_artella)
        project_folder_btn.clicked.connect(self.open_project_folder)
        sync_all_action.triggered.connect(partial(self.sync_all_assets, True, True))
        sync_characters_all_action.triggered.connect(partial(self.sync_category, 'Characters', 'all', True, True))
        sync_character_model_action.triggered.connect(partial(self.sync_category, 'Characters', 'model', True, False))
        sync_character_shading_action.triggered.connect(partial(self.sync_category, 'Characters', 'shading', True, False))
        sync_character_textures_action.triggered.connect(partial(self.sync_category, 'Characters', 'textures', True, False))
        sync_character_grooming_action.triggered.connect(partial(self.sync_category, 'Characters', 'groom', True, False))
        sync_background_elements_all_action.triggered.connect(partial(self.sync_category, 'BackgroundElements', 'all', True, True))
        sync_background_elements_model_action.triggered.connect(partial(self.sync_category, 'BackgroundElements', 'model', True, False))
        sync_background_elements_shading_action.triggered.connect(partial(self.sync_category, 'BackgroundElements', 'shading', True, False))
        sync_background_elements_textures_action.triggered.connect(partial(self.sync_category, 'BackgroundElements', 'textures', True, False))
        sync_props_all_action.triggered.connect(partial(self.sync_category, 'Props', 'all', True, True))
        sync_props_model_action.triggered.connect(partial(self.sync_category, 'Props', 'model', True, False))
        sync_props_shading_action.triggered.connect(partial(self.sync_category, 'Props', 'shading', True, False))
        sync_props_textures_action.triggered.connect(partial(self.sync_category, 'Props', 'textures', True, False))
        sync_sequences_action.triggered.connect(partial(self.sync_sequences, True, True))
        settings_btn.clicked.connect(self.open_settings)
        self.user_icon.user_info.updatedAvailability.connect(self.update_ui)

    def update_ui(self, artella_is_available):
        # TODO: This is called each time we check to Artella availability through user icon widget
        # TODO: If Artella is not enabled we should disable all the widgets of the UI and notify
        # TODO: the user that Artella server is not available right now

        return

    def closeEvent(self, event):
        self.cleanup()
        self.user_icon.destroy()                # We use it to clean timers stuff manually
        event.accept()

    @staticmethod
    def open_project_in_artella():
        sp.open_artella_project()

    @staticmethod
    def open_project_folder():
        pythonutils.open_folder(sp.get_solstice_project_path())

    def _sequencer_loaded(self):
        self._tab_widget.setTabText(1, 'Sequence Manager')
        self._tab_widget.setTabEnabled(1, True)
        self.stack.slide_in_next()

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)

    def _update_items(self, update=False):
        self._info_asset_widget.setVisible(False)
        self._asset_viewer.update_items(update=update)

        items = list()
        for i in range(self._asset_viewer.rowCount()):
            for j in range(self._asset_viewer.columnCount()):
                item = self._asset_viewer.cellWidget(i, j)
                if not item:
                    continue
                item = item.containedWidget.name
                items.append(item)

    def open_settings(self):
        """
        Opens Pipelinizer Settings Dialog
        """

        PipelinizerSettings(self)

    def sync_category(self, category, sync_type='all', full_sync=True, ask=False):
        """
        Synchronizes the given category located in Artella Server, if exists
        :param category:
        :param full_sync:
        :param sync_type:
        :param ask:
        :return:
        """

        if sync_type != 'all' and sync_type != 'model' and sync_type != 'shading' and sync_type != 'textures':
            sys.solstice.logger.error('Synchronization type {0} is not valid!'.format(sync_type))
            return

        start_time = time.time()
        try:
            cmds.waitCursor(state=True)
            elements = list()
            category_name = pythonutils.string_to_camel_case(category)
            thread, event = sys.solstice.info_dialog.do(
                'Getting Artella "{0}" Info ... Please wait!'.format(category_name),
                'SolsticeArtella{0}Thread'.format(category_name),
                self.get_assets_by_category, [category, True, elements])

            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.05)

            elements_to_sync = list()
            if elements:
                elements = elements[0]
                for i, el in enumerate(elements.expand_tree()):
                    if i == 0:
                        continue
                    if full_sync:
                        elements_to_sync.append(elements[el].tag)
                    else:
                        if not os.path.exists(elements[el].tag):
                            elements_to_sync.append(elements[el].tag)

                if len(elements_to_sync) > 0:
                    assets = list()
                    for el in elements_to_sync:
                        assets.append(base_asset.AssetWidget(
                            name=os.path.basename(el),
                            path=el
                        ))

                    if ask:
                        result = qtutils.show_question(
                            None,
                            'Some {0} are not synchronized locally'.format(category),
                            'Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                        if result == QMessageBox.No:
                            cmds.waitCursor(state=False)
                            return

                    for asset in assets:
                        asset.sync(sync_type=sync_type, ask=False)
                    # solstice_sync_dialog.SolsticeSyncPath(paths=elements_to_sync).sync()
        except Exception as e:
            sys.solstice.logger.debug(str(e))
            cmds.waitCursor(state=False)
        elapsed_time = time.time() - start_time
        sys.solstice.logger.debug('{0} synchronized in {1} seconds'.format(category_name, elapsed_time))
        cmds.waitCursor(state=False)

    def sync_sequences(self, full_sync=False, ask=False):
        """
        Synchronizes all the sequences of Solstice Short Film
        :param full_sync: bool, If True, all the assets will be sync with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no warranty that you have latest versions
               on other assets)
       :param ask: bool, True if you want to show a message box to the user to decide if the want or not download
               missing files in his local machine
        :return:
        """

        if ask:
            result = qtutils.show_question(None, 'Full synchronization', 'Do you want to synchronize all assets? NOTE: This can take quite a lot of time!')
            if result == QMessageBox.Yes:
                self.sequencer.sync_sequences()

    def sync_all_assets(self, full_sync=False, ask=False):
        """
        Synchronizes all the assets of Solstice Short Film
        :param full_sync: bool, If True, all the assets will be sync with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no warranty that you have latest versions
               on other assets)
       :param ask: bool, True if you want to show a message box to the user to decide if the want or not download
               missing files in his local machine
        :return:
        """

        if ask:
            result = qtutils.show_question(None, 'Full synchronization', 'Do you want to synchronize all assets? NOTE: This can take quite a lot of time!')
            if result == QMessageBox.Yes:
                self.sync_category(category='Characters', full_sync=full_sync, ask=False)
                self.sync_category(category='BackgroundElements', full_sync=full_sync, ask=False)
                self.sync_category(category='Props', full_sync=full_sync, ask=False)

    def update_asset_info(self, asset=None, check_published_info=None, check_working_info=None, check_lock_info=None):
        self._current_asset = asset
        if asset:
            if not check_published_info:
                check_published_info = False
                if self.settings.has_option(self.settings.app_name, 'auto_check_published'):
                    check_published_info = strtobool(self.settings.get('auto_check_published'))

            if not check_working_info:
                if self.settings.has_option(self.settings.app_name, 'auto_check_working'):
                    check_working_info = strtobool(self.settings.get('auto_check_working'))

            if not check_lock_info:
                if self.settings.has_option(self.settings.app_name, 'auto_check_lock'):
                    check_lock_info = strtobool(self.settings.get('auto_check_lock'))

            try:
                info_widget = asset.get_asset_info_widget(check_published_info=check_published_info, check_working_info=check_working_info, check_lock_info=check_lock_info)
            except Exception as e:
                msg = 'Impossible to retrieve info from Artella. Please try it later'
                cmds.warning(msg)
                sys.solstice.logger.debug(msg)
                sys.solstice.logger.error(str(e))
                return
            if not info_widget:
                return

            for i in reversed(range(self._info_asset_widget.layout().count())):
                self._info_asset_widget.layout().itemAt(i).widget().setParent(None)
            self._info_asset_widget.layout().addWidget(info_widget)
            self._info_asset_widget.setVisible(True)
        else:
            self._info_asset_widget.setVisible(False)

    @staticmethod
    def get_assets_by_category(category='Characters', only_assets=True, thread_result=None, thread_event=None):
        """
        Gets a list of assets of a specific category
        :param category: str
        :param only_assets: bool
        :return: list<str>
        """

        assets_path = sp.get_solstice_assets_path()
        chars_path = os.path.join(assets_path, category)
        st = artellautils.get_status(chars_path)

        tree = treelib.Tree()
        root = tree.create_node(chars_path, data=st)

        def get_assets(parent_node):
            if hasattr(parent_node.data, 'references'):
                for ref_name, ref_data in parent_node.data.references.items():
                    status = artellautils.get_status(ref_data.path)
                    if type(status) == artellaclasses.ArtellaDirectoryMetaData:
                        node=tree.create_node(ref_data.path, parent=parent_node, data=status)
                        get_assets(parent_node=node)
                    elif type(status) == artellaclasses.ArtellaAssetMetaData:
                        working_path = os.path.join(ref_data.path, '__working__')
                        status = artellautils.get_status(working_path)
                        node = tree.create_node(ref_data.path, parent=parent_node, data=status)
                        if not only_assets:
                            get_assets(parent_node=node)
                    else:
                        tree.create_node(ref_data.path, parent=parent_node, data=status)

        get_assets(root)
        # tree.show()

        if thread_event:
            thread_event.set()
            thread_result.append(tree)

        return tree

# ============================================================================================================


def run():
    # Check that Artella plugin is loaded and, if not, we loaded it
    artellautils.update_artella_paths()
    if not artellautils.check_artella_plugin_loaded():
        if not artellautils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    sp.update_solstice_project_path()

    # # Check if the current scene needs to save and ask user if the want to do it
    # needs_save = cmds.file(query=True, modified=True)
    # if needs_save:
    #     result = solstice_qt_utils.show_question(None, 'Current scene has unsaved changes', 'Before using Solstice Pipelinizer you should save your changes if you do not want to lose them. Do you want to save and continue?')
    #     if result == QMessageBox.Yes:
    #         cmds.SaveScene()

    win = Pipelinizer()
    win.show()

    win.sequencer.init_sequencer()
