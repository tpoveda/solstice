#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Initiailzer class for solstice_pipeline
# ==================================================================="""

import os
import re
import sys
import glob
import urllib2
import pkgutil
import datetime
import platform
import importlib
import webbrowser
from collections import OrderedDict
if sys.version_info[:2] > (2, 7):
    from importlib import reload
else:
    from imp import reload

import maya.cmds as cmds
import maya.mel as mel
import maya.utils

import solstice_pipeline

loaded_modules = OrderedDict()
reload_modules = list()
logger = None
info_dialog = None
settings = None
tray = None

# =================================================================================

solstice_project_id = '2/2252d6c8-407d-4419-a186-cf90760c9967/'
solstice_project_id_raw = '2252d6c8-407d-4419-a186-cf90760c9967'
solstice_project_id_full = '_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'
valid_categories = ['textures', 'model', 'shading', 'groom']            # NOTE: The order is important, textures MUST go first
valid_status = ['working', 'published']

# =================================================================================


def update_paths():
    root_path = os.path.dirname(os.path.abspath(__file__))
    extra_paths = [os.path.join(root_path, 'externals'), os.path.join(root_path, 'resources', 'icons')]
    for path in extra_paths:
        if os.path.exists(path) and path not in sys.path:
            print('Adding Path {} to SYS_PATH ...'.format(path))
            sys.path.append(path)
        else:
            print('Path {} not added to SYS_PATH because it does not exists or is already included in SYS_PATH!'.format(path))

    for subdir, dirs, files in os.walk(root_path):
        if subdir not in sys.path:
            sys.path.append(subdir)


def get_module_names():
    """
    Return the name of all solstice_tools modules
    :return: list<str>
    """

    root_path = os.path.dirname(os.path.abspath(__file__))
    root_name = os.path.basename(root_path)
    ret = list()
    for subdir, dirs, files in os.walk(root_path):
        file_names = glob.glob(os.path.split(subdir)[0] + '/*/__init__.py')
        for file_path in file_names:
            directories = file_path.split(os.sep)
            subdirectory = str.join(os.sep, directories[:directories.index(root_name)])
            package_path = file_path.split(subdirectory)[1].replace('\\', '.')[1:].replace('.__init__.py', '').replace('.__init__.pyc', '')
            ret.append(package_path)
    return ret


def import_modules():
    mod_names = list(set(get_module_names()))
    for mod_name in mod_names:
        if 'userSetup' in mod_name:
            continue
        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            logger.debug('Impossible to import {} module'.format(mod_name))
            logger.debug(str(e))

        try:
            mod = sys.modules[mod_name]
            imported_mods = list()
            for importer, mod_name, is_pkg in pkgutil.iter_modules(mod.__path__):
                if 'userSetup' in mod_name:
                    continue
                mod_name = '{0}.{1}'.format(mod.__name__, mod_name)
                imported_mod = importlib.import_module(mod_name)
                imported_mods.append(imported_mod)
                logger.debug('Module {} initialized!'.format(mod_name))
        except Exception as e:
            continue


def reload_all():
    """
    Loops through all solstice_tools modules and reload them ane by one
    Used to increase iteration times
    """

    for mod_name in get_module_names():
        try:
            if mod_name == 'solstice_pipeline':
                continue
            mod = sys.modules[mod_name]
            reload(mod)
        except Exception:
            continue


def create_solstice_logger():
    """
    Creates and initializes solstice logger
    """

    from solstice_utils import solstice_logger
    global logger
    logger = solstice_logger.Logger(name='solstice', level=solstice_logger.LoggerLevel.DEBUG)
    logger.debug('Initializing Solstice Tools ...')


def create_solstice_settings():
    """
    Creates a settings file that can be accessed globally by all tools
    """

    from solstice_pipeline.solstice_utils import solstice_config
    global settings
    settings = solstice_config.create_config('solstice_pipeline')


def create_solstice_info_window():
    """
    Creates a global window that is used to show different type of info
    """

    from solstice_gui import solstice_info_dialog
    global info_dialog
    info_dialog = solstice_info_dialog.InfoDialog()


def create_solstice_shelf():
    """
    Creates Solstice Tools shelf
    """

    solstice_pipeline.logger.debug('Building Solstice Tools Shelf ...')

    from solstice_gui import solstice_shelf

    try:
        s_shelf = solstice_shelf.SolsticeShelf()
        s_shelf.create(delete_if_exists=True)
        shelf_file = get_solstice_shelf_file()
        if shelf_file and os.path.isfile(shelf_file):
            s_shelf.build(shelf_file=shelf_file)
            s_shelf.set_as_active()
    except Exception as e:
        solstice_pipeline.logger.warning('Error during Solstice Shelf Creation: {}'.format(e))


def create_solstice_menu():
    """
    Create Solstice Tools menu
    """

    solstice_pipeline.logger.debug('Building Solstice Tools Menu ...')

    from solstice_gui import solstice_menu
    from solstice_utils import solstice_maya_utils

    try:
        solstice_maya_utils.remove_menu('Solstice')
    except Exception:
        pass

    try:
        s_menu = solstice_menu.SolsticeMenu()
        menu_file = get_solstice_menu_file()
        if menu_file and os.path.isfile(menu_file):
            s_menu.create_menu(file_path=menu_file, parent_menu='Solstice')
    except Exception as e:
        solstice_pipeline.logger.warning('Error during Solstice Menu Creation: {}'.format(e))


def create_solstice_tray():
    """
    Create Solstice Pipeline tray
    """

    solstice_pipeline.logger.debug('Creating Solstice Tray ...')

    from solstice_pipeline.solstice_gui import solstice_traymessage

    global tray
    tray = solstice_traymessage.SolsticeTrayMessage()


def update_solstice_project():
    """
    Set the current Maya project to the path where Solstice is located inside Artella folder
    """

    try:
        solstice_pipeline.logger.debug('Setting Solstice Project ...')
        solstice_project_folder = os.environ.get('SOLSTICE_PROJECT', 'folder-not-defined')
        if solstice_project_folder and os.path.exists(solstice_project_folder):
            cmds.workspace(solstice_project_folder, openWorkspace=True)
            solstice_pipeline.logger.debug('Solstice Project setup successfully! => {}'.format(solstice_project_folder))
        else:
            solstice_pipeline.logger.debug('Unable to set Solstice Project! => {}'.format(solstice_project_folder))
    except Exception as e:
        solstice_pipeline.logger.debug(str(e))


def update_solstice_project_path():
    """
    Updates environment variable that stores Solstice Project path and returns
    the stored path
    :return: str
    """

    artella_var = os.environ.get('ART_LOCAL_ROOT', None)
    if artella_var and os.path.exists(artella_var):
        os.environ['SOLSTICE_PROJECT'] = '{0}/_art/production/{1}'.format(artella_var, solstice_project_id)
    else:
        logger.debug('ERROR: Impossible to set Solstice Project Environment Variable! Contact TD please!')


def get_solstice_project_path():
    """
    Returns Solstice Project path
    :return: str
    """
    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        update_solstice_project_path()

    env_var = os.environ.get('SOLSTICE_PROJECT', None)
    if env_var is None:
        raise RuntimeError('Solstice Project not setted up properly. Is Artella running? Contact TD!')

    return os.environ.get('SOLSTICE_PROJECT')


def get_solstice_shelf_file():
    """
    Returns Solstice Shelf File
    :return: str
    """

    shelf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shelf.xml')
    if not os.path.exists(shelf_file):
        solstice_pipeline.logger.warning('Shelf file: {} does not exists!'.format(shelf_file))
        return False

    return shelf_file


def get_solstice_menu_file():
    """
    Returns Solstice Menu File
    :return: str
    """

    menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu.json')
    if not os.path.exists(menu_file):
        solstice_pipeline.logger.warning('Menu file: {} does not exists!'.format(menu_file))
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
            from solstice_pipeline.solstice_gui import solstice_sync_dialog
            solstice_sync_dialog.SolsticeSyncPath(paths=[assets_path]).sync()
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
            from solstice_pipeline.solstice_gui import solstice_sync_dialog
            solstice_sync_dialog.SolsticeSyncPath(paths=[production_path]).sync()
            return production_path
        except Exception as e:
            logger.debug('Error while synchronizing production path: {}'.format(e))
        return None


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


def init_solstice_environment_variables():
    """
    Initializes all necessary environment variables used in Solstice Tools
    """

    from solstice_pipeline.solstice_utils import solstice_artella_utils

    solstice_pipeline.logger.debug('Initializing environment variables for Solstice Tools ...')

    try:
        solstice_artella_utils.update_local_artella_root()
        artella_var = os.environ.get('ART_LOCAL_ROOT')
        solstice_pipeline.logger.debug('Artella environment variable is set to: {}'.format(artella_var))
        if artella_var and os.path.exists(artella_var):
            os.environ['SOLSTICE_PROJECT'] = '{}/_art/production/2/2252d6c8-407d-4419-a186-cf90760c9967/'.format(artella_var)
        else:
            solstice_pipeline.logger.debug('Impossible to set Artella environment variables! Solstice Tools wont work correctly! Please contact TD!')
    except Exception:
        solstice_pipeline.logger.debug('Error while setting Solstice Environment Variables. Solstice Tools may not work properly!')

    icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons')
    if os.path.exists(icons_path):
        if platform.system() == 'Darwin':
            os.environ['XBMLANGPATH'] = os.environ.get('XBMLANGPATH') + ':' + icons_path
        else:
            os.environ['XBMLANGPATH'] = os.environ.get('XBMLANGPATH') + ';' + icons_path
        solstice_pipeline.logger.debug('Artella Icons Folder "{}" added to Maya Icons Paths ...'.format(icons_path))
    else:
        solstice_pipeline.logger.debug('Solstice Icons not found! Solstice Shelf maybe will not show icons! Please contact TD!')

    solstice_pipeline.logger.debug('=' * 100)
    solstice_pipeline.logger.debug("Solstices Tools initialization completed!")
    solstice_pipeline.logger.debug('=' * 100)
    solstice_pipeline.logger.debug('*' * 100)
    solstice_pipeline.logger.debug('-' * 100)
    solstice_pipeline.logger.debug('\n')

    if os.environ.get('SOLSTICE_PIPELINE_SHOW'):
        from solstice_pipeline.solstice_tools import solstice_changelog
        solstice_changelog.run()


def update_tools():
    from solstice_pipeline.solstice_utils import solstice_download_utils
    solstice_download_utils.update_tools()


def message(msg, title='Solstice Tools'):
    if tray:
        tray.show_message(title=title, msg=msg)


def open_artella_project():
    """
    Opens Solstice Artella web page
    """

    project_url = 'https://www.artella.com/project/{0}/files'.format(solstice_project_id_raw)
    webbrowser.open(project_url)


def open_artella_documentation():
    """
    Opens Artella Documentation web page
    """

    documentation_url = 'https://solstice-short-film.gitbook.io/solstice/'
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
    try:
        return urllib2.urlopen('https://www.artella.com').getcode() == 200
    except:
        return False


def init():
    update_paths()
    create_solstice_logger()
    import_modules()
    reload_all()
    create_solstice_settings()
    init_solstice_environment_variables()
    create_solstice_info_window()
    create_solstice_shelf()
    create_solstice_menu()
    create_solstice_tray()
    update_solstice_project()

    if platform.system() == 'Darwin':
        from solstice_pipeline.solstice_tools import solstice_changelog
        solstice_changelog.run()
        cmds.evalDeferred('import solstice_pipeline; solstice_pipeline.update_tools()')


