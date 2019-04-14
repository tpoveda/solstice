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

import os
import re
import sys
import json
import urllib2
import datetime
import platform
import traceback
import webbrowser

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.dcc import dcc as abstractdcc

# =================================================================================

numbers = re.compile('\d+')

solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'
solstice_project_id_raw = '2252d6c8-407d-4419-a186-cf90760c9967'
solstice_project_id_full = '_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'
asset_types = ['Props', 'Background Elements', 'Characters']
valid_categories = ['textures', 'model', 'shading', 'groom']  # NOTE: The order is important, textures MUST go first
must_categories = ['textures', 'model', 'shading']            # NOTE: Categories that should be published to consider an asset published
valid_status = ['working', 'published']
ignored_paths = ['PIPELINE', 'lighting', 'Light Rigs', 'S_CH_02_summer_scripts']

# =================================================================================

dcc = abstractdcc.SolsticeDCC()
sys.solstice_dispatcher = None
logger = None
tray = None
settings = None
info_dialog = None

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


class SolsticePipeline(QObject):
    def __init__(self):
        super(SolsticePipeline, self).__init__()

        self.logger = self.create_solstice_logger()
        self.settings = self.create_solstice_settings()
        self.detect_dcc()
        self.update_paths()
        self.set_environment_variables()
        self.reload_all()

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

        from solstice.pipeline.utils import logger
        global logger
        logger = logger.Logger(name='solstice', level=logger.LoggerLevel.DEBUG)
        logger.debug('Initializing Solstice Tools ...')
        return logger

    @staticmethod
    def create_solstice_settings():
        """
        Creates a settings file that can be accessed globally by all tools
        """

        from solstice.pipeline.utils import config
        global settings
        settings = config.create_config('solstice_pipeline')
        return settings

    @staticmethod
    def create_solstice_info_window():
        """
        Creates a global window that is used to show different type of info
        """

        from solstice.pipeline.gui import infodialog
        global info_dialog
        info_dialog = infodialog.InfoDialog()
        return info_dialog

    @staticmethod
    def reload_all():
        # if os.environ.get('SOLSTICE_DEV_MODE', '0') == '1':
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
                    reload(module)
                except Exception as e:
                    logger.error('{} | {}'.format(e, traceback.format_exc()))

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
        from solstice.pipeline.tools import searcher
        searcher.SolsticeSearcher.install_hotkeys()

    def update_paths(self):
        """
        Updates system path with Solstice Tools Paths
        :return:
        """

        from solstice.pipeline.utils import artellautils

        root_path = os.path.dirname(os.path.abspath(__file__))
        extra_paths = [os.path.join(root_path, 'resources', 'icons'), os.path.join(root_path, 'externals', 'animBot')]
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

        for subdir, dirs, files in os.walk(root_path):
            if subdir not in sys.path:
                sys.path.append(subdir)

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
                os.environ['SOLSTICE_PROJECT'] = '{}/_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'.format(artella_var)
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
                self.logger.debug('Icon Path not found for DCC: {}'.format(dcc))
        else:
            self.logger.debug('Solstice Icons not found! Solstice Shelf maybe will not show icons! Please contact TD!')

        self.logger.debug('=' * 100)
        self.logger.debug("Solstices Tools initialization completed!")
        self.logger.debug('=' * 100)
        self.logger.debug('*' * 100)
        self.logger.debug('-' * 100)
        self.logger.debug('\n')

        if os.environ.get('SOLSTICE_PIPELINE_SHOW'):
            from solstice.pipeline.tools import hello
            hello.run()

    def detect_dcc(self):
        """
        Function that updates current DCC
        """

        global dcc

        try:
            import maya.cmds as cmds
            from solstice.pipeline.dcc import mayadcc
            dcc = mayadcc.SolsticeMaya()
        except ImportError:
            try:
                import hou
                from solstice.pipeline.dcc import houdinidcc
                dcc = houdinidcc.SolsticeHoudini()
            except ImportError:
                try:
                    import nuke
                    from solstice.pipeline.dcc import nukedcc
                    dcc = nukedcc.SolsticeNuke()
                except ImportError as e:
                    print(e)
                    print('No valid DCC found!')

        if dcc:
            self.logger.debug('Current DCC: {}'.format(dcc.get_name()))

        return dcc

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

        global tray
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
                logger.warning('Impossible to setup Solstice Project in DCC: {}'.format(dcc))
        except Exception as e:
            self.logger.debug(str(e))

# =================================================================================


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


def get_solstice_shelf_file():
    """
    Returns Solstice Shelf File
    :return: str
    """

    shelf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shelf.json')
    if not os.path.exists(shelf_file):
        logger.warning('Shelf file: {} does not exists!'.format(shelf_file))
        return False

    return shelf_file


def get_solstice_menu_file():
    """
    Returns Solstice Menu File
    :return: str
    """

    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    if not os.path.exists(menu_file):
        logger.warning('Menu file: {} does not exists!'.format(menu_file))
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
        logger.debug('Asset Path does not exists!: {0}'.format(assets_path))
        logger.debug('Trying to synchronize it ...')
        try:
            from solstice.pipeline.gui import syncdialog
            syncdialog.SolsticeSyncPath(paths=[assets_path]).sync()
            return assets_path
        except Exception as e:
            logger.debug('Error while synchronizing production path: {}'.format(e))
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
        logger.debug('Production Path does not exists!: {0}'.format(production_path))
        logger.debug('Trying to synchronize it ...')
        try:
            from solstice.pipeline.gui import syncdialog
            syncdialog.SolsticeSyncPath(paths=[production_path]).sync()
            return production_path
        except Exception as e:
            logger.debug('Error while synchronizing production path: {}'.format(e))
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
                            logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
                            continue
                    else:
                        if not os.path.isfile(asset_data_file):
                            logger.debug('Impossible to get info of asset "{0}". Aborting!'.format(asset_name))
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
        logger.warning('Multiple assets found with name: {}'.format(asset_to_search))

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
    logger.debug('Registering Asset Sync: {0} - {1}'.format(asset_name, sync_time))
    settings.set(settings.app_name, asset_name, str(sync_time))
    settings.update()
    return sync_time


def update_tools():
    from solstice.pipeline.utils import downloadutils
    downloadutils.update_tools()


def message(msg, title='Solstice Tools'):
    if sys.platform == 'win32':
        if tray:
            tray.show_message(title=title, msg=msg)
        else:
            logger.debug(str(msg))
    else:
        logger.debug(str(msg))


def open_artella_project():
    """
    Opens Solstice Artella web page
    """

    project_url = 'https://www.artella.com/project/{0}/files'.format(solstice_project_id_raw)
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

    if not dcc:
        return False

    return dcc.get_name() == SolsticeDCC.Maya


def is_houdini():
    """
    Returns whether current DCC is Houdini or not
    :return: bool
    """

    if not dcc:
        return False

    return dcc.get_name() == SolsticeDCC.Houdini


def is_nuke():
    """
    Returns whether current DC is Houdini or not
    :return: bool
    """

    if not dcc:
        return False

    return dcc.get_name() == SolsticeDCC.Nuke


def get_tag_data_nodes():
    tag_nodes = list()
    objs = dcc.all_scene_objects()
    for obj in objs:
        valid_tag_data = dcc.attribute_exists(node=obj, attribute_name='tag_type')
        if valid_tag_data:
            tag_type = dcc.get_attribute_value(node=obj, attribute_name='tag_type')
            if tag_type and tag_type == 'SOLSTICE_TAG':
                tag_nodes.append(obj)

    return tag_nodes


def get_tag_info_nodes(as_nodes=True):
    tag_info_nodes = list()
    objs = dcc.all_scene_objects()
    for obj in objs:
        valid_tag_info_data = dcc.attribute_exists(node=obj, attribute_name='tag_info')
        if valid_tag_info_data:
            tag_info_nodes.append(obj)

    return tag_info_nodes


def get_assets(as_nodes=True):

    from solstice.pipeline.core import node

    asset_nodes = list()

    abc_nodes = get_alembics(as_nodes=False, only_roots=True)

    # We find tag data nodes
    tag_data_nodes = get_tag_data_nodes()
    for tag_data in tag_data_nodes:
        cns = dcc.list_connections(node=tag_data, attribute_name='node')
        if cns:
            asset = cns[0]
            if asset in abc_nodes:
                continue
            if as_nodes:
                asset_nodes.append(node.SolsticeAssetNode(node=asset))
            else:
                asset_nodes.append(asset)

    # We find nodes with tag info attribute (Alembics)
    tag_info_nodes = get_tag_info_nodes()
    for tag_info in tag_info_nodes:
        tag_info_dict = dcc.get_attribute_value(node=tag_info, attribute_name='tag_info')
        if tag_info_dict:
            if as_nodes:
                if tag_info in abc_nodes:
                    continue
                asset_nodes.append(node.SolsticeAssetNode(node=tag_info))
            else:
                asset_nodes.append(tag_info)

    return asset_nodes


def get_alembics(as_nodes=True, only_roots=False):

    from solstice.pipeline.core import node

    all_alembic_roots = list()
    added_roots = list()

    abc_nodes = list()
    objs = dcc.all_scene_objects()
    for obj in objs:
        if dcc.node_type(obj) == 'AlembicNode':
            abc_nodes.append(obj)

    for abc in abc_nodes:
        cns = dcc.list_connections(abc, 'transOp')
        for cn in cns:
            cn_root = dcc.node_root(cn)
            if cn_root in added_roots:
                continue
            if dcc.attribute_exists(cn_root, 'tag_info'):
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




def init():
    sys.dispatcher = SolsticePipeline()
