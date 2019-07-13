#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Solstice Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

main = __import__('__main__')

import os
import re
import sys
import json
import locale
import shutil
import urllib2
import datetime
import platform
import tempfile
import traceback
import importlib
import webbrowser

from solstice.pipeline.externals import solstice_six
from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.resources import solstice_resources
from solstice.pipeline.dcc.core import dcc as abstractdcc, node as dccnode

# =================================================================================

numbers = re.compile('\d+')

separator = '_'
solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'
solstice_project_id_raw = '2252d6c8-407d-4419-a186-cf90760c9967'
solstice_project_id_full = '_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'
asset_types = ['Props', 'Background Elements', 'Characters']
asset_files = ['textures', 'model', 'proxy', 'rig', 'builder', 'shading', 'groom']
valid_categories = ['textures', 'model', 'shading', 'rig', 'groom']  # NOTE: The order is important, textures MUST go first
must_categories = ['textures', 'model', 'shading', 'rig']            # NOTE: Categories that should be published to consider an asset published
valid_status = ['working', 'published']
ignored_paths = ['PIPELINE', 'lighting', 'Light Rigs', 'S_CH_02_summer_scripts']
model_suffix = 'MODEL'
proxy_suffix = 'PROXY'
rig_suffix = 'RIG'

# =================================================================================

Node = dccnode.SolsticeNodeDCC

# =================================================================================


class SolsticeDCC(object):
    Maya = 'maya'
    Houdini = 'houdini'
    Nuke = 'nuke'


class DataVersions(object):
    LAYOUT = '0.0.1'
    ANIM = '0.0.1'
    FX = '0.0.1'
    LIGHTING = '0.0.1'


class DataExtensions(object):
    ABC = 'abc'
    LAYOUT = 'layout'
    ANIM = 'anim'
    FX = 'fx'
    LIGHTING = 'light'


class SolsticeConfig(dict):
    """
    Configuration parser for passing JSON files
    """

    @staticmethod
    def paths():
        """
        Returns all possible configuration paths
        :return: list(str)
        """

        cwd = os.path.dirname(__file__)
        paths = [os.path.join(cwd, 'config.json')]
        path = os.environ.get('SOLSTICE_CONFIG_PATH')
        path = path or os.path.join(cwd, 'custom_config.json')
        if not os.path.exists(path):
            cwd = os.path.dirname(os.path.dirname(cwd))
            path = os.path.join(cwd, 'custom_config.json')
        if os.path.exists(path):
            paths.append(path)

        return paths

    def read(self):
        """
        Reeds all paths and overwrite the keys with each successive file
        """

        self.clear()

        for p in self.paths():
            lines = list()

            # Don't read comments (//)
            with open(p) as f:
                for l in f.readlines():
                    if not l.strip().startswith('//'):
                        lines.append(l)

            data = '\n'.join(lines)
            if data:
                self.update(json.loads(data))


class SolsticePipeline(QObject):
    def __init__(self):
        super(SolsticePipeline, self).__init__()

        self.dcc = abstractdcc.SolsticeDCC()
        self.logger = None
        self.config = None
        self.settings = None
        self.info_dialog = None
        self.tray = None

        self.logger = self.create_solstice_logger()
        self.config = self.init_config()
        self.settings = self.create_solstice_settings()
        self.detect_dcc()

    def setup(self):
        self.update_paths()
        self.set_environment_variables()
        self.import_all()

        self.info_dialog = self.create_solstice_info_window()
        self.create_solstice_shelf()
        self.create_solstice_menu()
        self.tray = self.create_solstice_tray()
        self.update_solstice_project()
        self.show_changelog()
        self.init_searcher()

        if is_maya():
            from solstice.pipeline.utils import mayautils as utils
            utils.viewport_message('Solstice Pipeline Tools loaded successfully!')

    @staticmethod
    def create_solstice_logger():
        """
        Creates and initializes solstice logger
        """

        from solstice.pipeline.utils import logger as logger_utils
        logger = logger_utils.Logger(name='solstice', level=logger_utils.LoggerLevel.DEBUG)
        logger.debug('Initializing Solstice Tools ...')
        return logger

    def init_config(self):
        """
        Read and initializes Solstice settings
        """

        if not self.config:
            config = SolsticeConfig()
            config.read()
        else:
            return self.config

        return config

    @staticmethod
    def create_solstice_settings():
        """
        Creates a settings file that can be accessed globally by all tools
        """

        from solstice.pipeline.utils import settings as setting_utils
        settings = setting_utils.create_settings('solstice_pipeline')
        return settings

    @staticmethod
    def create_solstice_info_window():
        """
        Creates a global window that is used to show different type of info
        """

        from solstice.pipeline.gui import infodialog
        info_dialog = infodialog.InfoDialog()
        return info_dialog

    def import_all(self):
        import inspect
        scripts_dir = os.path.dirname(__file__)
        for key, module in sys.modules.items():
            try:
                module_path = inspect.getfile(module)
            except TypeError:
                continue
            if module_path == __file__:
                continue
            if module_path.startswith(scripts_dir):
                try:
                    importlib.import_module(module.__name__)
                except Exception as e:
                    self.logger.error('{} | {}'.format(e, traceback.format_exc()))

    @staticmethod
    def show_changelog():
        if is_maya():
            import maya.cmds as cmds
            if platform.system() == 'Darwin':
                from solstice.pipeline.tools import changelog
                changelog.run()
                cmds.evalDeferred('import solstice.pipeline as sp; sp.update_tools()')

    @staticmethod
    def init_searcher():
        from solstice.pipeline.tools.searcher import searcher
        searcher.SolsticeSearcher.install_hotkeys()

    def update_paths(self):
        """
        Updates system path with Solstice Tools Paths
        :return:
        """

        from solstice.pipeline.utils import artellautils

        root_path = os.path.dirname(os.path.abspath(__file__))
        extra_paths = [
            os.path.join(root_path, 'resources', 'icons'),
            get_externals_path(),
            os.path.join(get_externals_path(), 'solstice_studiolibrary', 'packages')
        ]
        for path in extra_paths:
            if os.path.exists(path) and path not in sys.path:
                self.logger.debug('Adding Path {} to SYS_PATH ...'.format(path))
                sys.path.append(path)
            else:
                self.logger.debug('Path {} not added to SYS_PATH because it does not exists or is already included in SYS_PATH!'.format(path))

        # We add Artella Paths if they are not already added
        scripts_folder = artellautils.get_artella_python_folder()
        if scripts_folder not in sys.path:
            sys.path.append(scripts_folder)

        externals_paths = [os.path.join(get_externals_path(), name) for name in os.listdir(get_externals_path()) if os.path.isdir(os.path.join(get_externals_path(), name)) ]

        for d in externals_paths:
            if d not in sys.path:
                sys.path.append(d)

        # for subdir, dirs, files in os.walk(root_path):
        #     if subdir not in sys.path:
        #         sys.path.append(subdir)

    def set_environment_variables(self):
        """
        Initializes all necessary environment variables used in Solstice Tools
        """

        from solstice.pipeline.utils import artellautils

        self.logger.debug('Initializing environment variables for Solstice Tools ...')

        try:
            artellautils.update_local_artella_root()
            artella_var = os.environ.get('ART_LOCAL_ROOT')
            self.logger.debug('Artella environment variable is set to: {}'.format(artella_var))
            if artella_var and os.path.exists(artella_var):
                os.environ['SOLSTICE_PROJECT'] = '{}_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'.format(artella_var)
            else:
                self.logger.debug('Impossible to set Artella environment variables! Solstice Tools wont work correctly! Please contact TD!')
        except Exception as e:
            self.logger.debug('Error while setting Solstice Environment Variables. Solstice Tools may not work properly!')
            self.logger.error('{} | {}'.format(e, traceback.format_exc()))

        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons')
        if os.path.exists(icons_path):
            if is_maya():
                if platform.system() == 'Darwin':
                    os.environ['XBMLANGPATH'] = os.environ.get('XBMLANGPATH') + ':' + icons_path
                else:
                    os.environ['XBMLANGPATH'] = os.environ.get('XBMLANGPATH') + ';' + icons_path
                self.logger.debug('Artella Icons Folder "{}" added to Maya Icons Paths ...'.format(icons_path))
            else:
                self.logger.debug('Icon Path not found for DCC: {}'.format(self.dcc))
        else:
            self.logger.debug('Solstice Icons not found! Solstice Shelf maybe will not show icons! Please contact TD!')

        self.logger.debug('=' * 100)
        self.logger.debug("Solstices Tools initialization completed!")
        self.logger.debug('=' * 100)
        self.logger.debug('*' * 100)
        self.logger.debug('-' * 100)
        self.logger.debug('\n')

        if os.environ.get('SOLSTICE_PIPELINE_SHOW'):
            from solstice.pipeline.tools.hello import hello
            hello.run()

    def detect_dcc(self):
        """
        Function that updates current DCC
        """

        if 'cmds' in main.__dict__:
            from solstice.pipeline.dcc.maya import mayadcc
            self.dcc = mayadcc.SolsticeMaya()
        elif 'hou' in main.__dict__:
            import hou
            from solstice.pipeline.dcc.houdini import houdinidcc
            self.dcc = houdinidcc.SolsticeHoudini()
        elif 'nuke' in main.__dict__:
            import nuke
            from solstice.pipeline.dcc.nuke import nukedcc
            self.dcc = nukedcc.SolsticeNuke()
        else:
            self.logger.error('No valid DCC found!')

        if self.dcc:
            self.logger.debug('Current DCC: {}'.format(self.dcc.get_name()))

        return self.dcc

    def create_solstice_shelf(self):
        """
        Creates Solstice Tools shelf
        """

        self.logger.debug('Building Solstice Tools Shelf ...')

        from solstice.pipeline.utils import shelf

        try:
            s_shelf = shelf.SolsticeShelf()
            s_shelf.create(delete_if_exists=True)
            shelf_file = get_solstice_shelf_file()
            if shelf_file and os.path.isfile(shelf_file):
                s_shelf.build(shelf_file=shelf_file)
                s_shelf.set_as_active()
        except Exception as e:
            self.logger.warning('Error during Solstice Shelf Creation: {} | {}'.format(e, traceback.format_exc()))

    def create_solstice_menu(self):
        """
        Create Solstice Tools menu
        """

        self.logger.debug('Building Solstice Tools Menu ...')

        from solstice.pipeline.utils import menu

        if is_maya():
            from solstice.pipeline.utils import mayautils
            try:
                mayautils.remove_menu('Solstice')
            except Exception:
                pass

        try:
            s_menu = menu.SolsticeMenu()
            menu_file = get_solstice_menu_file()
            if menu_file and os.path.isfile(menu_file):
                s_menu.create_menu(file_path=menu_file, parent_menu='Solstice')
        except Exception as e:
            self.logger.warning('Error during Solstice Menu Creation: {} | {}'.format(e, traceback.format_exc()))

    def create_solstice_tray(self):
        """
        Create Solstice Pipeline tray
        """

        from solstice.pipeline.gui import traymessage

        self.logger.debug('Creating Solstice Tray ...')
        tray = traymessage.SolsticeTrayMessage()
        return tray

    def update_solstice_project(self):
        """
        Set the current Maya project to the path where Solstice is located inside Artella folder
        """

        try:
            if is_maya():
                import maya.cmds as cmds
                self.logger.debug('Setting Solstice Project ...')
                solstice_project_folder = os.environ.get('SOLSTICE_PROJECT', 'folder-not-defined')
                if solstice_project_folder and os.path.exists(solstice_project_folder):
                    cmds.workspace(solstice_project_folder, openWorkspace=True)
                    self.logger.debug(
                        'Solstice Project setup successfully! => {}'.format(solstice_project_folder))
                else:
                    self.logger.debug('Unable to set Solstice Project! => {}'.format(solstice_project_folder))
            else:
                self.logger.warning('   Impossible to setup Solstice Project in DCC: {}'.format(self.dcc))
        except Exception as e:
            self.logger.debug(str(e))


# =================================================================================

def reload():
    for mod in sys.modules.keys():
        if mod in sys.modules and mod.startswith('solstice'):
            del sys.modules[mod]
    sys.solstice.import_all()
    sys.solstice.detect_dcc()


def update_solstice_project_path():
    """
    Updates environment variable that stores Solstice Project path and returns
    the stored path
    :return: str
    """

    from solstice.pipeline.utils import artellautils as artella

    artella_var = os.environ.get('ART_LOCAL_ROOT', None)
    if artella_var and os.path.exists(artella_var):
        os.environ['SOLSTICE_PROJECT'] = '{0}/_art/production/{1}'.format(artella_var, solstice_project_id)
    else:
        print('CONNECTING TO ARTELLA APP ...')
        artella.connect_artella_app_to_spigot()
        # logger.debug('ERROR: Impossible to set Solstice Project Environment Variable! Contact TD please!')


def get_solstice_project_path():
    """
    Returns Solstice Project path
    :return: str
    """

    from solstice.pipeline.utils import artellautils as artella

    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        update_solstice_project_path()

    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        try:
            if is_maya():
                artella.launch_artella_app()
                artella.load_artella_maya_plugin()
            update_solstice_project_path()
        except Exception as e:
            raise RuntimeError('Solstice Project not setted up properly. Is Artella running? Contact TD!')
        env_var = os.environ.get('SOLSTICE_PROJECT', None)
        if env_var is None:
            raise RuntimeError('Solstice Project not setted up properly. Is Artella running? Contact TD!')

    return os.environ.get('SOLSTICE_PROJECT')


def get_solstice_icons_path():
    """
    Returns path where Solstice icons are stored
    :return: str
    """

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons')


def get_solstice_changelog_file():
    """
    Returns Solstice Changelog file
    :return: str
    """

    changelog_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'changelog.json')
    if not os.path.isfile(changelog_file):
        sys.solstice.logger.warning('Changelof file: {} does not exists!'.format(changelog_file))
        return False

    return changelog_file


def get_solstice_shelf_file():
    """
    Returns Solstice Shelf File
    :return: str
    """

    shelf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shelf.json')
    if not os.path.exists(shelf_file):
        sys.solstice.logger.warning('Shelf file: {} does not exists!'.format(shelf_file))
        return False

    return shelf_file


def get_solstice_menu_file():
    """
    Returns Solstice Menu File
    :return: str
    """

    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    if not os.path.exists(menu_file):
        sys.solstice.logger.warning('Menu file: {} does not exists!'.format(menu_file))
        return False

    return menu_file


def get_solstice_assets_path():
    """
    Returns Solstice Project Assets path
    :return: str
    """

    assets_path = os.path.join(get_solstice_project_path(), 'Assets')
    if os.path.exists(assets_path):
        return assets_path
    else:
        sys.solstice.logger.debug('Asset Path does not exists!: {0}'.format(assets_path))
        sys.solstice.logger.debug('Trying to synchronize it ...')
        try:
            from solstice.pipeline.gui import syncdialog
            syncdialog.SolsticeSyncPath(paths=[assets_path]).sync()
            return assets_path
        except Exception as e:
            sys.solstice.logger.debug('Error while synchronizing production path: {}'.format(e))
        return None


def get_solstice_production_path():
    """
    Returns Solstice Project Production path
    :return: str
    """

    production_path = os.path.join(get_solstice_project_path(), 'Production')
    if os.path.exists(production_path):
        return production_path
    else:
        sys.solstice.logger.debug('Production Path does not exists!: {0}'.format(production_path))
        sys.solstice.logger.debug('Trying to synchronize it ...')
        try:
            from solstice.pipeline.gui import syncdialog
            syncdialog.SolsticeSyncPath(paths=[production_path]).sync()
            return production_path
        except Exception as e:
            sys.solstice.logger.debug('Error while synchronizing production path: {}'.format(e))
        return None


def get_solstice_shot_name_regex():
    """
    Returns Regex used to identify solstice shorts
    :return: str
    """

    return re.compile(r"(\A[^_]+_\d{2,2}_\d{2,3})")


def get_externals_path():
    """
    Returns to Solstice external files
    :return: str
    """

    root_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_path, 'externals')


def get_asset_version(name):
    """
    Returns the version of a specific given asset (model_v001, return [v001, 001, 1])
    :param name: str
    :return: list<str, int>
    """

    string_version = name[-4:]
    int_version = map(int, re.findall('\d+', string_version))[0]
    int_version_formatted = '{0:03}'.format(int_version)

    return [string_version, int_version, int_version_formatted]


def find_asset(asset_to_search, assets_path=None, update_if_data_not_found=False, simple_mode=False, as_checkable=False):
    """
    Returns an asset object
    :param asset_to_search: str
    :return: solstice_asset
    """

    from solstice.pipeline.core import syncdialog, asset
    from solstice.pipeline.utils import pythonutils

    if not assets_path:
        assets_path = get_solstice_assets_path()

    if not os.path.exists(assets_path):
        return

    found_assets = list()

    for root, dirs, files in os.walk(assets_path):
        if dirs and '__working__' in dirs:
            asset_path = os.path.normpath(root)
            asset_name = os.path.basename(root)

            if asset_to_search:
                if asset_to_search != asset_name:
                    continue

            asset_data_file = os.path.join(asset_path, '__working__', 'data.json')
            is_ignored = False
            for ignored in ignored_paths:
                if ignored in asset_data_file:
                    is_ignored = True
                    break
            if not is_ignored:
                if not os.path.isfile(asset_data_file):
                    if update_if_data_not_found:
                        syncdialog.SolsticeSyncFile(files=[asset_data_file]).sync()
                        if not os.path.isfile(asset_data_file):
                            sys.solstice.logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                            continue
                    else:
                        if not os.path.isfile(asset_data_file):
                            sys.solstice.logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                        continue

                asset_category = pythonutils.camel_case_to_string(os.path.basename(os.path.dirname(asset_path)))
                asset_data = pythonutils.read_json(asset_data_file)

                new_asset = asset.generate_asset_widget_by_category(
                    name=asset_name,
                    path=asset_path,
                    category=asset_category,
                    icon=asset_data['asset']['icon'],
                    icon_format=asset_data['asset']['icon_format'],
                    preview=asset_data['asset']['preview'],
                    preview_format=asset_data['asset']['preview_format'],
                    description=asset_data['asset']['description'],
                    simple_mode=simple_mode,
                    checkable=as_checkable
                )

                found_assets.append(new_asset)

    if asset_to_search and len(found_assets) > 1:
        sys.solstice.logger.warning('Multiple assets found with name: {}'.format(asset_to_search))

    if len(found_assets) > 1:
        return found_assets
    elif len(found_assets) == 1:
        return found_assets[0]


def find_all_assets(assets_path=None, update_if_data_not_found=False, simple_mode=False, as_checkable=False):
    """
    Return a list of all asset objects
    :param assets_path: str
    :param update_if_data_not_found: bool
    :param simple_mode: bool
    :param as_checkable: bool
    :return: list<solstice_asset>
    """

    if assets_path is None:
        assets_path = get_solstice_assets_path()

    return find_asset(asset_to_search=None, assets_path=assets_path, update_if_data_not_found=update_if_data_not_found, simple_mode=simple_mode, as_checkable=as_checkable)


def register_asset(asset_name):
    """
    Adds the given asset to the local registry of assets
    This register is used to check last time a user synchronized a specific asset
    :param asset_name: str, name of the asset to register
    :return: str, sync time
    """

    invalid_names = ['__working__']
    if asset_name in invalid_names:
        return

    now = datetime.datetime.now()
    sync_time = now.strftime("%m/%d/%Y %H:%M:%S")
    sys.solstice.logger.debug('Registering Asset Sync: {0} - {1}'.format(asset_name, sync_time))
    sys.solstice.settings.set(sys.solstice.settings.app_name, asset_name, str(sync_time))
    sys.solstice.settings.update()
    return sync_time


def update_tools():
    from solstice.pipeline.utils import downloadutils
    downloadutils.update_tools()


def message(msg, title='Solstice Tools'):
    if sys.platform == 'win32':
        if sys.solstice.tray:
            sys.solstice.tray.show_message(title=title, msg=msg)
        else:
            sys.solstice.logger.debug(str(msg))
    else:
        sys.solstice.logger.debug(str(msg))


def get_artella_project_url():
    """
    Returns URL of Artella project
    :return: str
    """

    return 'https://www.artella.com/project/{0}/files'.format(solstice_project_id_raw)


def open_artella_project():
    """
    Opens Solstice Artella web page
    """

    project_url = get_artella_project_url()
    webbrowser.open(project_url)


def open_production_tracker():
    """
    Open Solstice Production Tracker
    """

    production_url = 'https://docs.google.com/spreadsheets/d/1kUPsHsPJwVY0s9uEcZCwXb5rlwUiHezgRT_m4obldOM/edit#gid=0'
    webbrowser.open(production_url)


def open_artella_documentation():
    """
    Opens Artella Documentation web page
    """

    documentation_url = 'https://tpoveda.github.io/solstice/'
    webbrowser.open(documentation_url)


def open_solstice_web():
    """
    Open Official Solstice web page
    """

    solstice_url = 'http://www.solsticeshortfilm.com/'
    webbrowser.open(solstice_url)


def send_email(tool_info='Solstice Tools'):
    webbrowser.open("mailto:%s?subject=%s" % ('tpoveda@cgart3d.com', urllib2.quote(tool_info)))


def artella_is_available():
    """
    Returns whether Artelal is available or not
    :return: bool
    """

    try:
        return urllib2.urlopen('https://www.artella.com').getcode() == 200
    except Exception:
        return False


def get_version():
    """
    Returns Solstice Tools version
    :return: int
    """

    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            version_data = json.loads(f.read())
        current_version = version_data.get('version')
        if not current_version:
            raise Exception('Impossible to retrieve Solstice Tools version!')

        if numbers.findall(current_version):
            lastoccr_sre = list(numbers.finditer(current_version))[-1]
            lastoccr = lastoccr_sre.group()
            return lastoccr

    return 0


def is_maya():
    """
    Returns whether current DCC is Maya or not
    :return: bool
    """

    try:
        if not sys.solstice.dcc:
            return False

        return sys.solstice.dcc.get_name() == SolsticeDCC.Maya
    except Exception:
        return 'cmds' in main.__dict__


def is_houdini():
    """
    Returns whether current DCC is Houdini or not
    :return: bool
    """

    try:
        if not sys.solstice.dcc:
            return False

        return sys.solstice.dcc.get_name() == SolsticeDCC.Houdini
    except Exception:
        return 'houdini' in main.__dict__


def is_nuke():
    """
    Returns whether current DC is Houdini or not
    :return: bool
    """

    try:
        if not sys.solstice.dcc:
            return False

        return sys.solstice.dcc.get_name() == SolsticeDCC.Nuke
    except Exception:
        return 'nuke' in main.__dict__


def get_tag_data_nodes(as_node=False):

    from solstice.pipeline.core import node

    tag_nodes = list()
    objs = sys.solstice.dcc.all_scene_objects()
    for obj in objs:
        valid_tag_data = sys.solstice.dcc.attribute_exists(node=obj, attribute_name='tag_type')
        if valid_tag_data:
            tag_type = sys.solstice.dcc.get_attribute_value(node=obj, attribute_name='tag_type')
            if tag_type and tag_type == 'SOLSTICE_TAG':
                if as_node:
                    obj = node.SolsticeTagDataNode(node=obj)
                tag_nodes.append(obj)

    return tag_nodes


def get_tag_info_nodes(as_node=False):

    from solstice.pipeline.core import node

    tag_info_nodes = list()
    objs = sys.solstice.dcc.all_scene_objects()
    for obj in objs:
        valid_tag_info_data = sys.solstice.dcc.attribute_exists(node=obj, attribute_name='tag_info')
        if valid_tag_info_data:
            if as_node:
                tag_info = sys.solstice.dcc.get_attribute_value(node=obj, attribute_name='tag_info')
                obj = node.SolsticeTagDataNode(node=obj, tag_info=tag_info)
            tag_info_nodes.append(obj)

    return tag_info_nodes


def get_assets(as_nodes=True, allowed_types='all'):

    from solstice.pipeline.core import node

    asset_nodes = list()

    if not allowed_types:
        return asset_nodes

    abc_nodes = get_alembics(as_nodes=False, only_roots=True)

    # We find tag data nodes
    tag_data_nodes = get_tag_data_nodes(as_node=as_nodes)
    for tag_data in tag_data_nodes:
        asset = tag_data.get_asset()
        if asset is None or asset in abc_nodes:
            continue
        if allowed_types and allowed_types != 'all':
            asset_type = tag_data.get_types()
            if asset_type not in allowed_types:
                continue
            asset_nodes.append(asset)
        else:
            asset_nodes.append(asset)

    # We find nodes with tag info attribute (Alembics)
    tag_info_nodes = get_tag_info_nodes(as_node=as_nodes)
    for tag_info in tag_info_nodes:
        asset = tag_info.get_asset()
        if asset is None:
            continue
        if allowed_types and allowed_types != 'all':
            asset_type = tag_info.get_types()
            if asset_type not in allowed_types:
                continue
            if tag_info in abc_nodes:
                continue
            asset_nodes.append(asset)
        else:
            if tag_info in abc_nodes:
                continue
            asset_nodes.append(asset)

    return asset_nodes


def get_alembics(as_nodes=True, only_roots=False):

    from solstice.pipeline.core import node

    all_alembic_roots = list()
    added_roots = list()

    abc_nodes = list()
    objs = sys.solstice.dcc.all_scene_objects()
    for obj in objs:
        if sys.solstice.dcc.node_type(obj) == 'AlembicNode':
            abc_nodes.append(obj)

    for abc in abc_nodes:
        cns = sys.solstice.dcc.list_connections(abc, 'transOp')
        for cn in cns:
            cn_root = sys.solstice.dcc.node_root(cn)
            if cn_root in added_roots:
                continue
            if sys.solstice.dcc.attribute_exists(cn_root, 'tag_info'):
                if as_nodes:
                    if only_roots:
                        all_alembic_roots.append(node.SolsticeAssetNode(node=cn_root))
                    else:
                        all_alembic_roots.append((node.SolsticeAssetNode(node=cn_root), abc))
                else:
                    if only_roots:
                        all_alembic_roots.append(cn_root)
                    else:
                        all_alembic_roots.append((cn_root, abc))
                added_roots.append(cn_root)

    return all_alembic_roots


def format_path(format_string, path='', **kwargs):
    """
    Resolves the given string with the given path and keyword arguments
    :param format_string: str
    :param path: str
    :param kwargs: dict
    :return: str
    """

    from solstice.pipeline.utils import pythonutils

    sys.solstice.logger.debug('Format String: {}'.format(format_string))

    dirname, name, extension = pythonutils.split_path(path)
    encoding = locale.getpreferredencoding()
    temp = tempfile.gettempdir()
    if temp:
        temp = temp.decode(encoding)

    username = pythonutils.user()
    if username:
        username = username.decode(encoding)

    local = os.getenv('APPDATA') or os.getenv('HOME')
    if local:
        local = local.decode(encoding)

    kwargs.update(os.environ)

    labels = {
        "name": name,
        "path": path,
        "root": path,  # legacy
        "user": username,
        "temp": temp,
        "home": local,  # legacy
        "local": local,
        "dirname": dirname,
        "extension": extension,
    }

    kwargs.update(labels)

    resolved_string = solstice_six.u(str(format_string)).format(**kwargs)

    sys.solstice.logger.debug('Resolved string: {}'.format(resolved_string))

    return pythonutils.norm_path(resolved_string)


def temp_path(*args):
    """
    Returns the temp directory set in the config
    :param args:
    :return: str
    """

    from solstice.pipeline.utils import pythonutils

    temp = sys.solstice.config.get('tempPath')
    return pythonutils.norm_path(os.path.join(format_path(temp), *args))


def unresolve_path(path_to_unresolve):
    """
    Converts path to a valid Solstice unresolved path
    :param path_to_unresolve: str
    :return: str
    """

    path_to_unresolve = path_to_unresolve.replace('\\', '/')
    solstice_var = os.environ['SOLSTICE_PROJECT']
    if path_to_unresolve.startswith(solstice_var):
        path_to_unresolve = path_to_unresolve.replace(solstice_var, '$SOLSTICE_PROJECT/')

    return path_to_unresolve


def resolve_path(path_to_resolve):
    """
    Converts unresolved path to a valid full path
    :param path_to_resolve: str
    :return: str
    """

    path_to_resolve = path_to_resolve.replace('\\', '/')
    solstice_var = os.environ['SOLSTICE_PROJECT']
    if path_to_resolve.startswith('$SOLSTICE_PROJECT/'):
        path_to_resolve = path_to_resolve.replace('$SOLSTICE_PROJECT/', solstice_var)

    return path_to_resolve


def create_temp_path(name, clean=True, make_dirs=True):
    """
    Creates new temp directory with the given name
    :param name: str
    :param clean: bool
    :param make_dirs: bool
    :return: str
    """

    path = temp_path(name)
    if clean and os.path.exists(path):
        shutil.rmtree(path)

    if make_dirs and not os.path.exists(path):
        os.makedirs(path)

    return path


def init():
    sys.solstice = SolsticePipeline()
    sys.solstice.setup()


def load_shaders():
    """
    Function that loads all the shaders of the current scene
    """

    if not is_maya():
        return

    from solstice.pipeline.tools.shaderlibrary import shaderlibrary

    shaderlibrary.ShaderLibrary.load_all_scene_shaders()


def unload_shaders():
    """
    Function that uloads and removes all the shaders loaded of the current scene
    """

    if not is_maya():
        return

    from solstice.pipeline.tools.shaderlibrary import shaderlibrary

    shaderlibrary.ShaderLibrary.unload_shaders()


def solstice_save(notify=False):
    """
    Function that saves current file cleaning student license
    """

    from solstice.pipeline.utils import mayautils

    if is_maya():
        mayautils.clean_scene()

    sys.solstice.dcc.save_current_scene(force=False)

    if is_maya():
        mayautils.clean_student_line()

    if notify:
        sys.solstice.tray.show_message(title='Save File', msg='File saved successfully!')

    return True


def lock_file(file_path=None, notify=False):
    """
    Locks current file in Artella
    :param file_path: file to lock
    """

    from solstice.pipeline.utils import artellautils

    if not file_path:
        file_path = sys.solstice.dcc.scene_name()
        if not file_path:
            sys.solstice.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
            return False

    if not os.path.isfile(file_path):
        sys.solstice.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    artellautils.lock_file(file_path=file_path, force=True)
    if notify:
        sys.solstice.tray.show_message(title='Lock File', msg='File locked successfully!')

    return True


def unlock_file(file_path=None, notify=False):
    """
    Unlocks current file in Artella
    :param file_path:
    """

    from solstice.pipeline.utils import artellautils

    if not file_path:
        file_path = sys.solstice.dcc.scene_name()
        if not file_path:
            sys.solstice.logger.error('File {} cannot be unlocked because it does not exists!'.format(file_path))
            return False

    if not os.path.isfile(file_path):
        sys.solstice.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    msg = 'If changes in file: \n\n{}\n\n are not submitted to Artella yet, submit them before unlocking the file please. \n\n Do you want to continue?'.format(file_path)
    res = sys.solstice.dcc.confirm_dialog(title='Solstice Tools - Unlock File', message=msg, button=['Yes', 'No'], cancel_button='No', dismiss_string='No')
    if res != 'Yes':
        return False

    artellautils.unlock_file(file_path=file_path)
    if notify:
        sys.solstice.tray.show_message(title='Unlock File', msg='File unlocked successfully!')

    return True


def upload_working_version(file_path=None, notify=False):
    """
    Uploads a new version of the given file
    :param file_path: str
    """

    from solstice.pipeline.utils import artellautils

    if not file_path:
        file_path = sys.solstice.dcc.scene_name()

    if not file_path:
        sys.solstice.logger.warning('Impossible to make a new version of an empty file path. Open a scene located in Solstice Artella folder!')
        return

    if not file_path.startswith(get_solstice_assets_path()):
        sys.solstice.logger.warning('Impossible to make a new version of a file that is not located in Solstice Artella folder. Open a scene located in Solstice Artella folder!')
        return

    short_path = file_path.replace(get_solstice_assets_path(), '')[1:]

    history = artellautils.get_asset_history(file_path)
    file_versions = history.versions
    if not file_versions:
        current_version = 1
    else:
        current_version = 0
        for v in file_versions:
            if int(v[0]) > current_version:
                current_version = int(v[0])
        current_version += 1

    try:
        comment, res = QInputDialog.getMultiLineText(sys.solstice.dcc.get_main_window(), 'Make New Version ({}) : {}'.format(current_version, short_path), 'Comment')
    except Exception:
        comment, res = QInputDialog.getText(sys.solstice.dcc.get_main_window(), 'Make New Version ({}) : {}'.format(current_version, short_path), 'Comment')

    if res and comment:
        artellautils.upload_new_asset_version(file_path=file_path, comment=comment)

        if notify:
            sys.solstice.tray.show_message(title='New Working Version', msg='New Working version {} uploaded to Artella server succesfully!'.format(current_version))

        return True

    return False


def run_publisher():
    """
    Runs the publisher taking into account the current scene status
    :return:
    """

    print('Executing publisher tool ...')
