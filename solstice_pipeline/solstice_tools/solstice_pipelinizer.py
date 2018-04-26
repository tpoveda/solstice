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
from functools import partial

import pathlib2
import treelib

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_user, solstice_grid, solstice_asset, solstice_assetviewer, solstice_assetbrowser
from solstice_utils import solstice_python_utils, solstice_maya_utils, solstice_artella_utils, solstice_image
from resources import solstice_resource

from solstice_utils import solstice_artella_classes, solstice_qt_utils, solstice_browser_utils
from solstice_gui import solstice_label, solstice_breadcrumb, solstice_navigationwidget, solstice_filelistwidget, solstice_splitters


class Pipelinizer(solstice_windows.Window, object):

    title = 'Solstice Tools - Artella Pipeline'
    version = '1.0'
    docked = False

    solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'

    def __init__(self, name='PipelinizwerWindow', parent=None, **kwargs):

        self._projects = None
        super(Pipelinizer, self).__init__(name=name, parent=parent, **kwargs)
        # self.load_projects()

    def custom_ui(self):
        super(Pipelinizer, self).custom_ui()

        self.set_logo('solstice_pipeline_logo')

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
        settings_btn = QToolButton()
        settings_btn.setText('Settings')

        top_menu_layout.addWidget(artella_project_btn, 0, 0, 1, 1, Qt.AlignCenter)
        top_menu_layout.addWidget(project_folder_btn, 0, 1, 1, 1, Qt.AlignCenter)
        top_menu_layout.addWidget(settings_btn, 0, 2, 1, 1, Qt.AlignCenter)

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

        self._asset_viewer = solstice_assetviewer.AssetViewer(assets_path=self.get_solstice_assets_path(), update_asset_info_fn=self._update_asset_info)
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        asset_splitter.addWidget(self._asset_viewer)

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
            new_btn.toggled.connect(partial(self._update_items, category))
            categories_buttons[category] = new_btn
            categories_buttons[category].setCheckable(True)
            categories_menu_layout.addWidget(new_btn)
            self._categories_btn_group.addButton(new_btn)
        categories_buttons['All'].setChecked(True)

        self._asset_info_lbl = solstice_splitters.Splitter('')
        self._asset_icon = QLabel()
        self._asset_icon.setPixmap(solstice_resource.pixmap('empty_file', category='icons').scaled(200, 200, Qt.KeepAspectRatio))
        self._asset_icon.setAlignment(Qt.AlignCenter)
        self._asset_description = QTextEdit()
        self._asset_description.setReadOnly(True)
        info_asset_layout.addWidget(self._asset_info_lbl)
        info_asset_layout.addWidget(self._asset_icon)
        info_asset_layout.addLayout(solstice_splitters.SplitterLayout())
        info_asset_layout.addWidget(self._asset_description)

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
        # local_data_layout.setAlignment(Qt.AlignTop)
        local_data_widget.setLayout(local_data_layout)
        local_data_browser = solstice_assetbrowser.AssetBrowser(title='       Local Data      ', root_path=self.get_solstice_assets_path())
        local_data_layout.addWidget(local_data_browser)
        asset_viewer_splitter.addWidget(local_data_widget)

        # =================================================================================================

        #self.get_assets_by_category()

    def _update_items(self, category, flag):
        self._current_asset = None
        self._info_asset_widget.setVisible(False)
        self._asset_viewer.update_items(category)

    def _update_asset_info(self, asset=None):

        if self._current_asset:
            self._current_asset.toggle_asset_menu()
        self._current_asset = asset

        if asset:
            self._info_asset_widget.setVisible(True)
            self._asset_info_lbl.set_text(asset.name)
            if asset.icon is not None and asset.icon != '':
                self._asset_icon.setPixmap(QPixmap.fromImage(solstice_image.base64_to_image(asset.icon, image_format=asset.icon_format)).scaled(300, 300, Qt.KeepAspectRatio))
            self._asset_description.setText(asset.description)

        else:
            self._info_asset_widget.setVisible(False)

    def get_assets_by_category(self, category='Characters', only_assets=True):
        """
        Gets a list of assets of a specific category
        :param category: str
        :param only_assets: bool
        :return: list<str>
        """

        assets_path = self.get_solstice_assets_path()
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
        tree.show()
        return tree

        # category_folder = os.path.join(solstice_assets_path, category)
        # if not os.path.exists(category_folder):
        #     # TODO: Add messagebox to answer the user if they want to syncrhonize the category folder
        #     print('Category folder does not exists! Trying to retrieve it!')
        #     solstice_artella_utils.synchronize_path(category_folder)

    def load_projects(self):
        self._projects_btn.setMenu(None)
        self._projects_btn.setStyleSheet(
            """
            QPushButton::menu-indicator
            {
                subcontrol-position: right center;
            }
            """
        )
        menu = QMenu(self._projects_btn)

    @classmethod
    def update_solstice_project_path(cls):
        """
        Updates environment variable that stores Solstice Project path and returns
        the stored path
        :return: str
        """

        artella_var = os.environ.get('ART_LOCAL_ROOT', None)
        if artella_var and os.path.exists(artella_var):
            os.environ['SOLSTICE_PROJECT'] = '{0}/_art/production/{1}'.format(artella_var, cls.solstice_project_id)
        else:
            sp.logger.debug('ERROR: Impossible to set Solstice Project Environment Variable! Contact TD please!')

    @classmethod
    def get_solstice_project_path(cls):
        """
        Returns Solstice Project path
        :return: str
        """
        env_var = os.environ.get('SOLSTICE_PROJECT', None)
        if env_var is None:
            cls.update_solstice_project_path()

        env_var = os.environ.get('SOLSTICE_PROJECT', None)
        if env_var is None:
            raise RuntimeError('Solstice Project not setted up properly. Is Artella running? Contact TD!')

        return os.environ.get('SOLSTICE_PROJECT')

    @classmethod
    def get_solstice_assets_path(cls):
        """
        Returns Solstice Project Assets path
        :return: str
        """

        assets_path = os.path.join(cls.get_solstice_project_path(), 'Assets')
        if os.path.exists(assets_path):
            sp.logger.debug('Getting Assets Path: {0}'.format(assets_path))
            return assets_path
        else:
            sp.logger.debug('Asset Path does not exists!: {0}'.format(assets_path))
            return None

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

    # Check that Artella plugin is loaded and, if not, we loaded it
    solstice_artella_utils.update_artella_paths()
    if not solstice_artella_utils.check_artella_plugin_loaded():
        if not solstice_artella_utils.load_artella_maya_plugin():
            pass

    # Update Solstice Project Environment Variable
    Pipelinizer.update_solstice_project_path()

    current_directory = pathlib2.Path(Pipelinizer.get_solstice_project_path()).glob('**/*')
    files = [x for x in current_directory if x.is_file()]
    for f in files:
        print(f)

    # dct = solstice_python_utils.path_to_dictionary(path=Pipelinizer.get_solstice_project_path())
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
