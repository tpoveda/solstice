#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_pipelinizer.py
# by Tomas Poveda
# Solstice Pipeline tool to smooth the workflow between Maya and Artella
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import time
from functools import partial
from distutils.util import strtobool

import pathlib2
import treelib

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_user, solstice_grid, solstice_asset, solstice_assetviewer, solstice_assetbrowser, solstice_published_info_widget, solstice_sync_dialog
from solstice_utils import solstice_python_utils, solstice_maya_utils, solstice_artella_utils, solstice_image
from resources import solstice_resource

from solstice_utils import solstice_artella_classes, solstice_qt_utils, solstice_browser_utils
from solstice_gui import solstice_label, solstice_breadcrumb, solstice_navigationwidget, solstice_filelistwidget, solstice_splitters


class PipelinizerSettings(QDialog, object):
    def __init__(self, settings, parent=None):
        super(PipelinizerSettings, self).__init__(parent=parent)

        self._settings = settings

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

        self._auto_check_cbx = QCheckBox('Auto Check Versions?')
        frame_layout.addWidget(self._auto_check_cbx)

        main_layout.addLayout(solstice_splitters.SplitterLayout())

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(1)
        main_layout.addLayout(bottom_layout)

        save_btn = QPushButton('Save')
        cancel_btn = QPushButton('Cancel')
        bottom_layout.addWidget(save_btn)
        bottom_layout.addWidget(cancel_btn)

        self.exec_()


class Pipelinizer(solstice_windows.Window, object):

    name = 'Pipelinizer'
    title = 'Solstice Tools - Artella Pipeline'
    version = '1.0'
    docked = False

    def __init__(self, name='PipelinizwerWindow', parent=None, **kwargs):

        self._projects = None
        super(Pipelinizer, self).__init__(name=name, parent=parent, **kwargs)
        # self.load_projects()

    def custom_ui(self):
        super(Pipelinizer, self).custom_ui()

        self.set_logo('solstice_pipeline_logo')

        if self.settings.config_file.exists():
            if not self.settings.has_option(self.settings.app_name, 'auto_check'):
                self.settings.set(self.settings.app_name, 'auto_check', str(False))
                self.settings.update()

        self._current_asset = None

        self._toolbar = QToolBar('Tools', self)
        self._toolbar.setAllowedAreas(Qt.RightToolBarArea | Qt.LeftToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.RightToolBarArea, self._toolbar)

        user_icon = solstice_user.UserWidget(name='Summer', role='Director')
        user_icon.move(1100, 0)
        user_icon.setStyleSheet("QWidget{background: transparent;}");
        self._logo_scene.addWidget(user_icon)

        top_menu_layout = QGridLayout()
        top_menu_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(top_menu_layout)
        artella_project_btn = QToolButton()
        artella_project_btn.setText('Artella')
        project_folder_btn = QToolButton()
        project_folder_btn.setText('Project')
        synchronize_btn = QToolButton()
        synchronize_btn.setText('Synchronize')
        synchronize_btn.setPopupMode(QToolButton.InstantPopup)
        settings_btn = QToolButton()
        settings_btn.setText('Settings')

        # TODO: Create gobal settings file and simple file dialog editor

        synchronize_menu = QMenu(self)
        sync_characters_action = QAction('Characters', self)
        sync_props_action = QAction('Props', self)
        sync_background_elements_action = QAction('Background Elements', self)
        for action in [sync_characters_action, sync_props_action, sync_background_elements_action]:
            synchronize_menu.addAction(action)
        synchronize_btn.setMenu(synchronize_menu)

        for i, btn in enumerate([artella_project_btn, project_folder_btn, synchronize_btn, settings_btn]):
            top_menu_layout.addWidget(btn, 0, i, 1, 1, Qt.AlignCenter)

        tab_widget = QTabWidget()
        tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tab_widget.setMinimumHeight(330)
        self.main_layout.addWidget(tab_widget)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        categories_widget.setLayout(categories_layout)

        asset_browser_widget = QWidget()
        asset_browser_layout = QHBoxLayout()
        asset_browser_layout.setContentsMargins(0, 0, 0, 0)
        asset_browser_layout.setSpacing(0)
        asset_browser_widget.setLayout(asset_browser_layout)

        sequences_widget = QWidget()
        sequences_layout = QVBoxLayout()
        sequences_layout.setContentsMargins(0, 0, 0, 0)
        sequences_layout.setSpacing(0)
        sequences_widget.setLayout(sequences_layout)

        tab_widget.addTab(categories_widget, 'Assets Manager')
        tab_widget.addTab(asset_browser_widget, ' Assets Browser ')
        tab_widget.addTab(sequences_widget, 'Sequences Manager')

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

        self._asset_viewer = solstice_assetviewer.AssetViewer(
            assets_path=sp.get_solstice_assets_path(),
            item_prsesed_callback=self._update_asset_info)
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

        # ================== Asset Browser Widget
        asset_viewer_splitter = QSplitter(Qt.Horizontal)
        asset_browser_layout.addWidget(asset_viewer_splitter)

        artella_server_widget = QWidget()
        artella_server_layout = QHBoxLayout()
        artella_server_layout.setContentsMargins(0, 0, 0, 0)
        artella_server_layout.setSpacing(0)
        # artella_server_layout.setAlignment(Qt.AlignTop)
        artella_server_widget.setLayout(artella_server_layout)
        artella_server_browser = solstice_assetbrowser.AssetBrowser(title='Artella Server Data')
        artella_server_layout.addWidget(artella_server_browser)
        asset_viewer_splitter.addWidget(artella_server_widget)

        local_data_widget = QWidget()
        local_data_layout = QHBoxLayout()
        local_data_layout.setContentsMargins(0, 0, 0, 0)
        local_data_layout.setSpacing(0)
        local_data_layout.setAlignment(Qt.AlignTop)
        local_data_widget.setLayout(local_data_layout)
        local_data_browser = solstice_assetbrowser.AssetBrowser(title='       Local Data      ', root_path=sp.get_solstice_assets_path())
        local_data_layout.addWidget(local_data_browser)
        asset_viewer_splitter.addWidget(local_data_widget)

        # =================================================================================================
        sync_background_elements_action.triggered.connect(self.sync_background_elements)
        sync_characters_action.triggered.connect(self.sync_characters)
        settings_btn.clicked.connect(self._open_settings)
        # =================================================================================================

    def _change_category(self, category, flag):
        self._asset_viewer.change_category(category=category)

    def _update_items(self, update=False):
        self._current_asset = None
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

    def _open_settings(self):
        PipelinizerSettings(self.settings)

    def sync_background_elements(self, full_sync=True, ask=False):
        """
        Synchronizes all background elements located in Artella Server
         :param full_sync: bool, If True, all the assets will be sync with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no warranty that you have latest versions
               on other assets)
        :param ask: bool, True if you want to show a message box to the user to decide if the want or not download
                          missing files in his local machine
        """

        start_time = time.time()
        try:
            cmds.waitCursor(state=True)
            elements = list()
            thread, event = sp.info_dialog.do('Getting Artella Background Elements Info ... Please wait!', 'SolsticeArtellaBackgroundElements', self.get_assets_by_category, ['BackgroundElements', True, elements])
            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.25)
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
                if ask:
                    result = solstice_qt_utils.show_question(None,'Some background elements are not synchronized locally','Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                    if result == QMessageBox.Yes:
                        solstice_sync_dialog.SolsticeSyncPath(paths=elements_to_sync).sync()
                else:
                    solstice_sync_dialog.SolsticeSyncPath(paths=elements_to_sync).sync()
        except Exception as e:
            sp.logger.debug(str(e))
            cmds.waitCursor(state=False)
        elapsed_time = time.time() - start_time
        sp.logger.debug('Background Elements synchronized in {0} seconds'.format(elapsed_time))
        cmds.waitCursor(state=False)

    def sync_characters(self, full_sync=True, ask=False):
        """
        Synchronizes all characters located in Artella Server
         :param full_sync: bool, If True, all the assets will be sync with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no warranty that you have latest versions
               on other assets)
        :param ask: bool, True if you want to show a message box to the user to decide if the want or not download
                          missing files in his local machine
        """

        start_time = time.time()
        try:
            cmds.waitCursor(state=True)
            characters = list()
            thread, event = sp.info_dialog.do('Getting Artella Characters Info ... Please wait!', 'SolsticeArtellaCharacters', self.get_assets_by_category, ['Characters', True, characters])
            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.25)
                characters_to_sync = list()
            if characters:
                characters = characters[0]
                for i, ch in enumerate(characters.expand_tree()):
                    if i == 0:
                        continue
                    if full_sync:
                        characters_to_sync.append(characters[ch].tag)
                    else:
                        if not os.path.exists(characters[ch].tag):
                            characters_to_sync.append(characters[ch].tag)
            if len(characters_to_sync) > 0:
                if ask:
                    result = solstice_qt_utils.show_question(None, 'Some characters are not synchronized locally','Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                    if result == QMessageBox.Yes:
                        solstice_sync_dialog.SolsticeSyncPath(paths=characters_to_sync).sync()
                else:
                    solstice_sync_dialog.SolsticeSyncPath(paths=characters_to_sync).sync()
        except Exception as e:
            sp.logger.debug(str(e))
            cmds.waitCursor(state=False)
        elapsed_time = time.time() - start_time
        sp.logger.debug('Characters synchronized in {0} seconds'.format(elapsed_time))
        cmds.waitCursor(state=False)

    def sync_all_assets(self, full_sync=False, ask=False):
        """
        Synchronizes all the assets of Solstice Short Film
        :param full_sync: bool, If True, all the assets will be syncrhonized with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no waranty that you have latests versions
               on other assets)
        :return:
        """

        # Characters Synchronization
        cmds.waitCursor(state=True)
        characters = list()
        start_time = time.time()
        thread, event = sp.info_dialog.do('Getting Artella Characters Info ... Please wait!', 'SolsticeArtellaChars', self.get_assets_by_category, ['Characters', True, characters])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.25)
        characters_to_sync = list()
        if characters:
            characters = characters[0]
            for i, ch in enumerate(characters.expand_tree()):
                if i == 0:
                    continue
                if full_sync:
                    characters_to_sync.append(characters[ch].tag)
                else:
                    if not os.path.exists(characters[ch].tag):
                        characters_to_sync.append(characters[ch].tag)
        if len(characters_to_sync) > 0:
            if ask:
                result = solstice_qt_utils.show_question(None, 'Some characters are not synchronized locally', 'Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                if result == QMessageBox.Yes:
                    solstice_sync_dialog.SolsticeSyncPath(paths=characters_to_sync).sync()
            else:
                solstice_sync_dialog.SolsticeSyncPath(paths=characters_to_sync).sync()
        elapsed_time = time.time() - start_time
        sp.logger.debug('Characters synchronized in {0} seconds'.format(elapsed_time))

        # Props synchronization
        props = list()
        start_time = time.time()
        thread, event = sp.info_dialog.do('Getting Artella Props Info ... Please wait!', 'SolsticeArtellaProps', self.get_assets_by_category, ['Props', True, props])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.25)
        props_to_sync = list()
        if props:
            props = props[0]
            for i, pr in enumerate(props.expand_tree()):
                if i == 0:
                    continue
                if full_sync:
                    props_to_sync.append(props[pr].tag)
                else:
                    if not os.path.exists(props[pr].tag):
                        props_to_sync.append(props[pr].tag)
        if len(props_to_sync) > 0:
            if ask:
                result = solstice_qt_utils.show_question(None, 'Some props are not synchronized locally', 'Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                if result == QMessageBox.Yes:
                    solstice_sync_dialog.SolsticeSyncPath(paths=props_to_sync).sync()
            else:
                solstice_sync_dialog.SolsticeSyncPath(paths=props_to_sync).sync()
        elapsed_time = time.time() - start_time
        sp.logger.debug('Props synchronized in {0} seconds'.format(elapsed_time))

        # Background Elements Synchronization
        elements = list()
        start_time = time.time()
        thread, event = sp.info_dialog.do('Getting Artella Background Elements Info ... Please wait!', 'SolsticeArtellaBackgroundElements', self.get_assets_by_category, ['BackgroundElements', True, elements])
        while not event.is_set():
            QCoreApplication.processEvents()
            event.wait(0.25)
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
            if ask:
                result = solstice_qt_utils.show_question(None, 'Some background elements are not synchronized locally', 'Do you want to synchronize them? NOTE: This can take quite a lot of time!')
                if result == QMessageBox.Yes:
                    solstice_sync_dialog.SolsticeSyncPath(paths=elements_to_sync).sync()
            else:
                solstice_sync_dialog.SolsticeSyncPath(paths=elements_to_sync).sync()
        elapsed_time = time.time() - start_time
        sp.logger.debug('Background Elements synchronized in {0} seconds'.format(elapsed_time))
        cmds.waitCursor(state=False)

    def _update_asset_info(self, asset=None):

        self._current_asset = asset
        if asset:
            info_widget = asset.get_asset_info_widget()
            if not info_widget:
                return

            for i in reversed(range(self._info_asset_widget.layout().count())):
                self._info_asset_widget.layout().itemAt(i).widget().setParent(None)
            self._info_asset_widget.layout().addWidget(info_widget)
            self._info_asset_widget.setVisible(True)
        else:
            self._info_asset_widget.setVisible(False)

    def get_assets_by_category(self, category='Characters', only_assets=True, thread_result=None, thread_event=None):
        """
        Gets a list of assets of a specific category
        :param category: str
        :param only_assets: bool
        :return: list<str>
        """

        assets_path = sp.get_solstice_assets_path()
        chars_path = os.path.join(assets_path, category)
        st = solstice_artella_utils.get_status(chars_path)

        tree = treelib.Tree()
        root = tree.create_node(chars_path, data=st)

        def get_assets(parent_node):
            if hasattr(parent_node.data, 'references'):
                for ref_name, ref_data in parent_node.data.references.items():
                    status = solstice_artella_utils.get_status(ref_data.path)
                    if type(status) == solstice_artella_classes.ArtellaDirectoryMetaData:
                        node=tree.create_node(ref_data.path, parent=parent_node, data=status)
                        get_assets(parent_node=node)
                    elif type(status) == solstice_artella_classes.ArtellaAssetMetaData:
                        working_path = os.path.join(ref_data.path, '__working__')
                        status = solstice_artella_utils.get_status(working_path)
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

        # category_folder = os.path.join(solstice_assets_path, category)
        # if not os.path.exists(category_folder):
        #     # TODO: Add messagebox to answer the user if they want to syncrhonize the category folder
        #     print('Category folder does not exists! Trying to retrieve it!')
        #     solstice_artella_utils.synchronize_path(category_folder)

    @classmethod
    def get_asset_version(cls, name):
        """
        Returns the version of a specific given asset (model_v001, return [v001, 001, 1])
        :param name: str
        :return: list<str, int>
        """

        string_version = name[-4:]
        int_version = map(int, re.findall('\d+', string_version))[0]
        int_version_formatted = '{0:03}'.format(int_version)

        return [string_version, int_version, int_version_formatted]


def run():
    reload(solstice_python_utils)
    reload(solstice_maya_utils)
    reload(solstice_artella_classes)
    reload(solstice_artella_utils)
    reload(solstice_browser_utils)
    reload(solstice_image)
    reload(solstice_qt_utils)
    reload(solstice_resource)
    reload(solstice_user)
    reload(solstice_grid)
    reload(solstice_asset)
    reload(solstice_assetviewer)
    reload(solstice_assetbrowser)
    reload(solstice_label)
    reload(solstice_breadcrumb)
    reload(solstice_navigationwidget)
    reload(solstice_filelistwidget)
    reload(solstice_splitters)
    reload(solstice_published_info_widget)

    # Check that Artella plugin is loaded and, if not, we loaded it
    solstice_artella_utils.update_artella_paths()
    if not solstice_artella_utils.check_artella_plugin_loaded():
        if not solstice_artella_utils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    sp.update_solstice_project_path()

    # current_directory = pathlib2.Path(sp.get_solstice_project_path()).glob('**/*')
    # files = [x for x in current_directory if x.is_file()]
    # for f in files:
    #     print(f)

    # dct = solstice_python_utils.path_to_dictionary(path=sp.get_solstice_project_path())
    # print(dct)
    #
    # metadata = solstice_artella_utils.get_metadata()

    #
    # uri = solstice_artella_utils.get_cms_uri_current_file()
    # spigot = solstice_artella_utils.get_spigot_client()
    # rsp = spigot.execute(command_action='do', command_name='history', payload=uri)
    # rsp = spigot.execute(command_action='do', command_name='explore', payload=uri)
    # rsp = spigot.execute(command_action='do', command_name='checkout', payload=uri)
    # rsp = spigot.execute(command_action='do', command_name='unlock', payload=uri)
    # print(rsp)

    # solstice_artella_utils.get_status_current_file()

    # // solstice: {u'meta': {u'content_length': u'529', u'status': u'OK',
    #                         u'container_uri': u'/production/2/2252d6c8-407d-4419-a186-cf90760c9967/Assets/Characters/S_CH_02_summer',
    #                         u'content_type': u'application/json', u'date': u'Wed, 18 Apr 2018 00:45:44 GMT',
    #                         u'release_name': u'rig_v001', u'type': u'container_file',
    #                         u'file_path': u'rig/S_CH_02_summer_RIG.ma'},
    #               u'data': {
    #     u'rig/S_CH_02_summer_RIG.ma': {u'locked_view': u'0b51b5c2-eb9e7144-8f92-11e7-8af3-3e1fea15fa15',
    #                                    u'locked': True, u'locked_by': u'fc6d3b61-1ede-458c-aa0c-ad8343ee66ac',
    #                                    u'view_version': 15, u'relative_path': u'rig/S_CH_02_summer_RIG.ma',
    #                                    u'maximum_version': 16,
    #                                    u'lockedByDisplay': u'fc6d3b61-1ede-458c-aa0c-ad8343ee66ac',
    #                                    u'view_version_digest': u'e475f0a9755d9a28ab3275dabdea58cbe0be6734da8b135e045f83058913c033'}}
    #               } //

    # ret = QMessageBox().question(solstice_maya_utils.get_maya_window(), 'Artella Plugin not loaded!', 'Do you want to select manually where Artella Plugin is located?')
        # if ret == QMessageBox.Yes:
        #     artella_installation = os.path.join(os.getenv('PROGRAMDATA'), 'Artella')
        #     artella_plugin_path = QFileDialog.getOpenFileName(solstice_maya_utils.get_maya_window(), 'Select Artella Plugin', artella_installation, 'Python Files (*.py)')
        #     print(artella_plugin_path)
        #     return
        # else:
        #     return

    Pipelinizer.run()
