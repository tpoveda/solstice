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

import pathlib2
from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows, solstice_user, solstice_grid, solstice_asset, solstice_assetviewer
from solstice_utils import solstice_python_utils, solstice_maya_utils, solstice_artella_utils, solstice_artella_classes
from resources import solstice_resource


class Pipelinizer(solstice_windows.Window, object):

    title = 'Solstice Tools - Artella Pipeline'
    version = '1.0'
    docked = False

    solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'

    def __init__(self, name='PipelinizwerWindow', parent=None, **kwargs):

        self._projects = None
        super(Pipelinizer, self).__init__(name=name, parent=parent, **kwargs)
        self.load_projects()

    def custom_ui(self):
        super(Pipelinizer, self).custom_ui()

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.main_layout.addLayout(title_layout)

        self.logo_view = QGraphicsView()
        self.logo_view.setMaximumHeight(100)
        logo_scene = QGraphicsScene()
        logo_scene.setSceneRect(QRectF(0, 0, 2000, 100))
        self.logo_view.setScene(logo_scene)
        self.logo_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.logo_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.logo_view.setFocusPolicy(Qt.NoFocus)

        title_background_pixmap = solstice_resource.pixmap(name='solstice_pipeline', extension='png')
        solstice_logo_pixmap = solstice_resource.pixmap(name='solstice_pipeline_logo', extension='png')
        title_background = logo_scene.addPixmap(title_background_pixmap)
        solstice_logo = logo_scene.addPixmap(solstice_logo_pixmap)
        solstice_logo.setOffset(930, 0)

        user_icon = solstice_user.UserWidget(name='Summer', role='Director')
        user_icon.move(1100, 0)
        user_icon.setStyleSheet("QWidget{background: transparent;}");
        logo_scene.addWidget(user_icon)

        title_layout.addWidget(self.logo_view)

        top_menu_layout = QGridLayout()
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

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(2, 2, 2, 2)
        top_layout.setSpacing(2)
        self._projects_btn = QPushButton('No Project')
        self._projects_btn.setMinimumHeight(30)
        self._projects_btn.setMenu(None)
        top_layout.addWidget(self._projects_btn)
        self.main_layout.addLayout(top_layout)

        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(330)
        self.main_layout.addWidget(tab_widget)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(0)
        categories_widget.setLayout(categories_layout)

        tree_widget = QWidget()
        tree_layout = QHBoxLayout()
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        tree_widget.setLayout(tree_layout)

        tab_widget.addTab(categories_widget, 'Categories')
        tab_widget.addTab(tree_widget, '   Folders   ')

        # ================== Categoriew widget
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

        self._asset_viewer = solstice_assetviewer.AssetViewer()
        self._asset_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_categories_menu_layout.addWidget(self._asset_viewer)

        categories = ['All', 'Background Elements', 'Characters', 'Props', 'Sets']
        categories_buttons = dict()
        for category in categories:
            categories_buttons[category] = QPushButton(category)
            categories_menu_layout.addWidget(categories_buttons[category])

        # ================== Folder widget
        tree_views_splitter = QSplitter(Qt.Horizontal)
        tree_layout.addWidget(tree_views_splitter)

        tree_model = QFileSystemModel()
        tree_model.setRootPath(self.get_solstice_project_path())
        tree_view = QTreeView()
        tree_view.setModel(tree_model)
        tree_view.setRootIndex(tree_model.index(self.get_solstice_project_path()))
        tree_views_splitter.addWidget(tree_view)

        list_view = QListView()
        list_view.setMinimumWidth(150)
        tree_views_splitter.addWidget(list_view)

        # =================================================================================================

        self.get_assets_by_category()

    def get_assets_by_category(self, category='Sets//S_BG_01_gardenWinter_SnowHigh'):
        """
        Gets a list of assets of a specific category
        :param category: str
        :return: list<str>
        """

        ppath = self.get_solstice_assets_path()
        status = solstice_artella_utils.get_status(ppath)

        for ref_name, ref_data in status.references.items():
            print(ref_name)


        # solstice_assets_path = self.get_solstice_assets_path()
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

        return os.environ.get('SOLSTICE_PROJECT', None)

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

    # def resizeEvent(self, event):
    #     Pipelinizer.resizeEvent(self, event)
    #
    #     # TODO: Take the width from the QGraphicsView not hardcoded :)
    #     self.logo_view.centerOn(1000, 0)

        # opt = QStyleOptionSlider()
        # self.logo_view.horizontalScrollBar().initStyleOption(opt)
        # style = self.logo_view.horizontalScrollBar().style()
        # handle = style.subControlRect(style.CC_ScrollBar, opt, style.SC_ScrollBarSlider)
        # sliderPos = handle.center()
        # self.logo_view.horizontalScrollBar().setValue((1800 * 0.5) - sliderPos.x() * 0.5)

def run():
    reload(solstice_python_utils)
    reload(solstice_maya_utils)
    reload(solstice_artella_classes)
    reload(solstice_artella_utils)
    reload(solstice_resource)
    reload(solstice_user)
    reload(solstice_grid)
    reload(solstice_asset)
    reload(solstice_assetviewer)

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
