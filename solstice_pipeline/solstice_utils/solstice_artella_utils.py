#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_artella_utils.py
# by Tomas Poveda
# Utility module that contains useful utilities  and classes related
#  with Artella
# ______________________________________________________________________
# ==================================================================="""

import os
import sys
import json
import urllib2
import platform
try:
    import psutil
except:
    pass

from solstice_qt.QtWidgets import *

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_maya_utils as utils
from solstice_pipeline.solstice_utils import solstice_artella_classes as classes

artella_maya_plugin_name = 'Artella.py'
artella_app_name = 'lifecycler'
artella_root_prefix = '$ART_LOCAL_ROOT'
artella_web = 'https://www.artella.com'
artella_cms_url = 'https://cms-static.artella.com'

spigot_client = None

# ---------------------------------------------------------------------------------------


def update_artella_paths():
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    artella_folder = get_artella_data_folder()

    sp.logger.debug('Updating Artella paths from: {0}'.format(artella_folder))
    if artella_folder is not None and os.path.exists(artella_folder):
        for subdir, dirs, files in os.walk(artella_folder):
            if subdir not in sys.path:
                sp.logger.debug('Adding Artella path: {0}'.format(subdir))
                sys.path.append(subdir)


def update_local_artella_root():
    """
    Updates the environment variable that stores the Artella Local Path
    NOTE: This is done by Artella plugin when is loaded, so we should not do it manually again
    """

    metadata = get_metadata()
    if metadata:
        metadata.update_local_root()


def check_artella_plugin_loaded():
    """
    Returns True if the Artella plugin is loaded in Maya or False otherwise
    :return: bool
    """

    return cmds.pluginInfo('Artella', query=True, loaded=True)


def get_artella_data_folder():
    """
    Returns last version Artella folder installation
    :return: str
    """

    if platform.system() == 'Darwin':
        artella_folder = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'Artella')
    else:
        artella_folder = os.path.join(os.getenv('PROGRAMDATA'), 'Artella')

    artella_app_version = None
    version_file = os.path.join(artella_folder, 'version_to_run_next')
    if os.path.isfile(version_file):
        with open(version_file) as f:
            artella_app_version = f.readline()

    if artella_app_version is not None:
        artella_folder = os.path.join(artella_folder, artella_app_version)
    else:
        artella_folder = [os.path.join(artella_folder, name) for name in os.listdir(artella_folder) if os.path.isdir(os.path.join(artella_folder, name)) and name != 'ui']
        if len(artella_folder) == 1:
            artella_folder = artella_folder[0]
        else:
            sp.logger.info('Artella folder not found!')

    sp.logger.debug('ARTELLA FOLDER: {}'.format(artella_folder))
    if not os.path.exists(artella_folder):
        QMessageBox.information(None, 'Artella App Folder {} does not exists! Please contact Solstice TD!')

    return artella_folder


def get_artella_plugins_folder():
    """
    Returns folder where Artelle stores its plugins
    :return: str
    """

    return os.path.join(get_artella_data_folder(), 'plugins')


def get_artella_dcc_plugin(dcc='maya'):
    """
    Gets Artella DCC plugin depending of the given dcc string
    :param dcc: str, "maya" or "nuke"
    :return: str
    """

    return os.path.join(get_artella_plugins_folder(), dcc)


def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    artella_folder = os.path.dirname(get_artella_data_folder())
    return os.path.join(artella_folder, artella_app_name)


def get_artella_program_folder():
    """
    Returns folder where Artella shortcuts are located
    :return: str
    """

    # TODO: This only works on Windows, find a cross-platform way of doing this

    return os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Artella')


def get_artella_launch_shortcut():
    """
    Returns path where Launch Artella shortcut is located
    :return: str
    """

    # TODO: This only works on Windows, find a cross-platform way of doing this

    return os.path.join(get_artella_program_folder(), 'Launch Artella.lnk')


def launch_artella_app():
    """
    Executes Artella App
    """

    # TODO: This should not work in MAC, find a cross-platform way of doing this

    if os.name == 'mac':
        sp.logger.info('Launch Artella App: does not supports MAC yet')
        QMessageBox.information(None, 'Solstice Tools do not support automatically Artella Launch for Mac. Please close Maya, launch Artella manually, and start Maya again!')
        artella_app_file = get_artella_app() + '.bundle'
    else:
        #  Executing Artella executable directly does not work
        # artella_app_file = get_artella_app() + '.exe'
        artella_app_file = get_artella_launch_shortcut()

    artella_app_file = artella_app_file
    sp.logger.info('Artella App File: {0}'.format(artella_app_file))

    if os.path.isfile(artella_app_file):
        sp.logger.info('Launching Artella App ...')
        sp.logger.debug('Artella App File: {0}'.format(artella_app_file))
        os.startfile(artella_app_file.replace('\\', '//'))


def close_all_artella_app_processes(console):
    """
    Closes all Artella app (lifecycler.exe) processes
    :return:
    """

    # TODO: This only works with Windows and has a dependency on psutil library
    # TODO: Find a cross-platform way of doing this
    try:
        for proc in psutil.process_iter():
            if proc.name() == artella_app_name + '.exe':
                sp.logger.debug('Killing Artella App process: {}'.format(proc.name()))
                proc.kill()
        return True
    except:
        sp.logger.error('Impossible to close Artella app instances because psutil library is not available!')
        return False


def connect_artella_app_to_spigot(cli=None):
    """
    Creates a new Spigot Client instance and makes it to listen
    to our current installed (and launched) Artella app
    """

    # TODO: Check if Artella App is launched and, is not, launch it

    if cli is None:
        cli = get_spigot_client()

    artella_app_identifier = get_artella_app_identifier()

    cli.listen(artella_app_identifier, artella.passMsgToMainThread)

    return cli


def load_artella_maya_plugin():
    """
    Loads the Artella plugin in the current Maya session
    :return: bool
    """

    sp.logger.debug('Loading Artella Maya Plugin ...')
    artella_maya_plugin_folder = get_artella_dcc_plugin(dcc='maya')
    artella_maya_plugin_file = os.path.join(artella_maya_plugin_folder, artella_maya_plugin_name)
    if os.path.isfile(artella_maya_plugin_file):
        if not cmds.pluginInfo(artella_maya_plugin_name, query=True, loaded=True):
            cmds.loadPlugin(artella_maya_plugin_file)
            return True

    return False


def get_spigot_client():
    """
    Creates, connects and returns an instance of the Spigot client
    :return: SpigotClient
    """

    global spigot_client
    if spigot_client is None:
        utils.force_stack_trace_on()
        from am.artella.spigot.spigot import SpigotClient
        spigot_client = SpigotClient()
        connect_artella_app_to_spigot(spigot_client)
    return spigot_client


def get_artella_app_identifier():
    """
    Returns the installed Artella App identifier
    :return: variant, str || None
    """

    app_identifier = os.environ.get('ARTELLA_APP_IDENTIFIER', None)
    if app_identifier is None:
        maya_version = cmds.about(version=True).split()[0]
        app_identifier = 'maya.{0}'.format(maya_version)

    return app_identifier


def fix_path_by_project(path, fullpath=False):
    """
    Fix given path and updates to make it relative to the Artella project
    :param path: str, path to be fixed
    :return: str
    """

    project_path = sp.get_solstice_project_path()
    new_path = path.replace(project_path, artella_root_prefix+'\\')
    if fullpath:
        new_path = path.replace(project_path, artella_root_prefix+'/'+sp.solstice_project_id_full)
    return new_path


def get_metadata():
    """
    Returns Artella App MetaData
    :return: ArtellaMetaData
    """

    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='getMetaData', payload='{}')
    sp.logger.debug(rsp)
    rsp = json.loads(rsp)

    metadata = classes.ArtellaAppMetaData(
        cms_web_root=rsp['cms_web_root'],
        local_root=rsp['local_root'],
        storage_id=rsp['storage_id'],
        token=rsp['token']
    )

    return metadata


def get_status(file_path, as_json=False):
    """
    Returns the status of  the given file path
    :param file_path: str
    :return: str
    """

    uri = get_cms_uri(file_path)
    if not uri:
        sp.logger.info('Unable to get cmds uri from path: {}'.format(file_path))
        return False

    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='status', payload=uri)
    if isinstance(rsp, basestring):
        try:
            rsp = json.loads(rsp)
        except Exception:
            msg = 'Artella is not available at this moment ... Restart Maya and try again please!'
            sp.logger.error(msg)
            sp.message(msg)
            return {}

    if as_json:
        return rsp

    # Artella is down!!!!!
    if not rsp:
        return None

    if 'data' in rsp:
        if '_latest'in rsp['data']:
            # if 'SEQ' not in rsp['meta']['container_uri']:
            status_metadata = classes.ArtellaAssetMetaData(metadata_path=file_path, status_dict=rsp)
            return status_metadata

        status_metadata = classes.ArtellaDirectoryMetaData(metadata_path=file_path, status_dict=rsp)
    else:
        status_metadata = classes.ArtellaHeaderMetaData(header_dict=rsp['meta'])

    return status_metadata


def get_cms_uri_current_file():
    """
    Returns the CMS uri of the current file
    :return: str
    """

    current_file = cmds.file(query=True, sceneName=True)
    sp.logger.debug('Getting CMS Uri of file {0}'.format(current_file))

    cms_uri = artella.getCmsUri(current_file)
    if not cms_uri:
        sp.logger.error('Unable to get CMS uri from path: {0}'.format(current_file))
        return False

    sp.logger.debug('Retrieved CMS uri: {0}'.format(cms_uri))
    req = json.dumps({'cms_uri': cms_uri})

    return req


def get_cms_uri(path):
    """
    Returns the CMS uri of the given path, if exists
    :param path: str
    :return: dict
    """

    cms_uri = artella.getCmsUri(path)
    if not cms_uri:
        sp.logger.error('Unable to get CMS uri from path: {0}'.format(path))
        return False

    req = json.dumps({'cms_uri': cms_uri})
    return req


def get_status_current_file():
    """
    Returns the status of the current file
    :return:
    """

    current_file = cmds.file(query=True, sceneName=True)
    sp.logger.debug('Getting Artella Status of file {0}'.format(current_file))

    status = get_status(current_file)
    sp.logger.debug('{0} STATUS -> {1}'.format(current_file, status))

    return status


def explore_file(path):
    """
    Opens the current file in the file explorer
    :param path: str
    """

    uri = get_cms_uri(path)
    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='explore', payload=uri)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    return rsp


def synchronize_path(path):
    """
    Synchronize all the content of the given path, if exists
    :param path: str
    """

    uri =  get_cms_uri(path)
    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='updateCollection', payload=uri)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def synchronize_file(file_path):
    """
    Synchronize the specific given file, if exists
    :param file_path: str
    :return:
    """

    # TODO: We need to check if Artella App is running, if not abort the operation

    uri = get_cms_uri(file_path)
    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='update', payload=uri)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def get_asset_history(file_path, as_json=False):
    """
    Returns the history info of the given file, if exists
    :param file_path: str
    """

    uri = get_cms_uri(file_path)
    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='history', payload=uri)

    try:
        if isinstance(rsp, basestring):
            rsp = json.loads(rsp)
    except Exception as e:
        msg = 'Error while getting file history info: {}'.format(rsp)
        sp.logger.error(msg)
        sp.logger.error(str(e))
        return {}

    sp.logger.debug(rsp)

    if as_json:
        return rsp

    if 'data' in rsp:
        file_metadata = classes.ArtellaFileMetaData(file_dict=rsp)
        return file_metadata

    return rsp


def get_asset_image(asset_path, project_id):
    """
    Returns the asset image from Artella server
    :param asset_path: str, path of the asset relative to the Assets folder
    :param project_id: str, ID of the Artella project you are currently working
    :return:
    """

    # TODO: Authentication problem when doing request: look for workaround
    image_url = os.path.join('https://cms-static.artella.com/cms_browser/thumbcontainerAvatar', project_id, asset_path)
    print(image_url)
    data = urllib2.urlopen(image_url).read()


def launch_maya(file_path, maya_version=2017):
    """
    :param file_path: str
    :param maya_version: int
    :return:
    """

    spigot = get_spigot_client()

    payload = dict()
    payload['appName'] = "maya.{0}".format(str(maya_version))
    payload['parameter'] = "\"{0}\"".format(file_path)
    payload['wait'] = "60"
    payload = json.dumps(payload)
    rsp = spigot.execute(command_action='do', command_name='launchApp', payload=payload)
    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)
    sp.logger.debug(rsp)


def open_file_in_maya(file_path, maya_version=2017):
    """
    Open the given path in the given Maya version
    :param file_path: str
    :param maya_version: int
    """

    spigot = get_spigot_client()

    # Firt we try to open the app if its not launched
    launch_maya(file_path=file_path, maya_version=maya_version)

    # Now we open the file
    payload = dict()
    payload['appId'] = "maya.{0}".format(str(maya_version))
    payload['message'] = "{\"CommandName\":\"open\",\"CommandArgs\":{\"path\":\""+file_path+"\"}}".replace('\\', '/')
    payload['message'] = payload['message'].replace('\\', '/').replace('//', '/')
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='passToApp', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def import_file_in_maya(file_path, maya_version=2017):
    """
    Import the given asset path in the given Maya version current scene
    :param file_path: str
    :param maya_version: int
    """

    spigot = get_spigot_client()

    payload = dict()
    payload['appId'] = "maya.{0}".format(str(maya_version))
    payload['message'] = "{\"CommandName\":\"import\",\"CommandArgs\":{\"path\":\""+file_path+"\"}}".replace('\\', '/')
    payload['message'] = payload['message'].replace('\\', '/').replace('//', '/')
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='passToApp', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def reference_file_in_maya(file_path, maya_version=2017):
    """
    Import the given asset path in the given Maya version current scene
    :param file_path: str
    :param maya_version: int
    """

    spigot = get_spigot_client()

    payload = dict()
    payload['appId'] = "maya.{0}".format(str(maya_version))
    payload['message'] = "{\"CommandName\":\"reference\",\"CommandArgs\":{\"path\":\""+file_path+"\"}}".replace('\\', '/')
    payload['message'] = payload['message'].replace('\\', '/').replace('//', '/')
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='passToApp', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def is_published(file_path):
    """
    Returns whether an absolute file path refers to a published asset
    :param file_path: str, absolute path to a file
    :return: bool
    """

    rsp = get_status(file_path=file_path, as_json=True)
    meta = rsp.get('meta', {})
    if meta.get('status') != 'OK':
        sp.logger.info('Status is not OK: {}'.format(meta))
        return False

    return 'release_name' in meta


def is_locked(file_path):
    """
    Returns whether an absolute file path refers to a locked asset in edit mode, and if the file is locked
    by the current storage workspace
    :param file_path: str, absolute path to a file
    :return: bool
    """

    rsp = get_status(file_path=file_path)
    if rsp:
        if isinstance(rsp, classes.ArtellaDirectoryMetaData):
            if rsp.header.status != 'OK':
                sp.logger.info('Status is not OK: {}'.format(rsp))
                return False, False

            file_path = rsp.header.file_path or ''
            if not file_path or file_path == '':
                sp.logger.info('File path not found in response: {}'.format(rsp))
                return False, False

            for ref, ref_data in rsp.references.items():
                file_data = ref_data.path
                if not file_data:
                    sp.logger.info('File data not found in response: {}'.format(rsp.get('data', {}), ))
                    return
                if ref_data.locked:
                    user_id = get_current_user_id()
                    return True, user_id == ref_data.locked_view
        elif isinstance(rsp, classes.ArtellaHeaderMetaData):
            if rsp.status != 'OK':
                sp.logger.info('Status is not OK: {}'.format(rsp))
                return False, False

            file_path_header = rsp.file_path or ''
            if not file_path_header or file_path_header == '':
                sp.logger.info('File path not found in response: {}'.format(rsp))
                return False, False

            # This happens when we are trying to lock a file that has not been uploaded to Artella yet
            return None, None

    return False, False


def lock_file(file_path=None, force=False):
    """
    Locks given file path
    :param file_path: str
    :param force: bool
    """

    if not file_path:
        file_path = cmds.file(query=True, sceneName=True)
    if not file_path:
        sp.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    file_published = is_published(file_path=file_path)
    if file_published:
        msg = 'Current file ({}) is published and cannot be edited'.format(os.path.basename(file_path))
        sp.logger.info(msg)
        sp.message(msg)
        cmds.confirmDialog(title='Solstice Tools - Cannot Lock File', message=msg, button=['OK'])
        return False

    in_edit_mode, is_locked_by_me = is_locked(file_path=file_path)
    can_write = os.access(file_path, os.W_OK)
    if not can_write and is_locked_by_me:
        msg = 'Unable to check local write permissions for file: {}'.format(file_path)
        sp.logger.info(msg)
        sp.message(msg)

    if in_edit_mode is None and is_locked_by_me is None:
        msg = 'File is not versioned yet! '
        sp.logger.info(msg)
        return True

    if in_edit_mode and not is_locked_by_me:
        msg = 'Locked by another user or workspace or file is not uploaded to Artella yet: {}'.format(os.path.basename(file_path))
        sp.logger.info(msg)
        cmds.warning(msg)
        return False
    elif force or not in_edit_mode:
        result = 'Yes'
        if not force and not in_edit_mode:
            msg = '{} needs to be in Edit mode to save your file. Would like to turn edit mode on now?'.format(os.path.basename(file_path))
            sp.logger.info(msg)
            sp.message(msg)
            result = cmds.confirmDialog(title='Solstice Tools - Lock File', message=msg, button=['Yes', 'No'], cancelButton='No', dismissString='No')
        if result != 'Yes':
            return False

    spigot = get_spigot_client()
    payload = dict()
    payload['cms_uri'] = artella.getCmsUri(file_path)
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='checkout', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug('Server checkout response: {}'.format(rsp))

    if rsp.get('meta', {}).get('status') != 'OK':
        msg = 'Failed to lock {}'.format(os.path.basename(file_path))
        sp.logger.info(msg)
        cmds.warning(msg)
        cmds.confirmDialog(title='Solstice Tools - Failed to Lock File', message=msg, button=['OK'])
        return False

    return True


def upload_file(file_path, comment):
    spigot = get_spigot_client()
    payload = dict()
    cms_uri = artella.getCmsUri(file_path)
    if not cms_uri.startswith('/'):
        cms_uri = '/' + cms_uri
    payload['cms_uri'] = cms_uri
    payload['comment'] = comment
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='upload', payload=payload)
    if isinstance(rsp, basestring) or type(rsp) == str:
        rsp = json.loads(rsp)

    if rsp.get('status', {}).get('meta', {}).get('status') != 'OK':
        msg = 'Failed to publish version to Artella {}'.format(os.path.basename(file_path))
        sp.logger.info(msg)
        cmds.warning(msg)
        cmds.confirmDialog(title='Solstice Tools - Failed to Upload Bug. Restart Solstice Tools please!', message=msg, button=['OK'])
        return False

    return True


def get_current_user_id():
    metadata = get_metadata()
    if not metadata:
        return None
    return metadata.storage_id


def can_unlock(file_path):
    asset_status = get_status(file_path=file_path)
    if not asset_status:
        return
    asset_info = asset_status.references.values()[0]
    locker_name = asset_info.locked_view
    user_id = get_current_user_id()

    if locker_name is not None and locker_name != user_id:
        return False

    return True


def unlock_file(file_path):
    """
    Unlocks a given file path
    :param file_path:
    """

    spigot = get_spigot_client()
    payload = dict()
    payload['cms_uri'] = artella.getCmsUri(file_path)
    payload = json.dumps(payload)

    if not can_unlock(file_path=file_path):
        sp.logger.debug('Impossible to unlock file. File is locked by other user!')
        return

    rsp = spigot.execute(command_action='do', command_name='unlock', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    # if rsp.get('status', {}).get('meta', {}).get('status') != 'OK':

    if rsp:
        if rsp.get('meta', {}).get('status') != 'OK':
            msg = 'Failed to unlock {}'.format(os.path.basename(file_path))
            sp.logger.info(msg)
            return False
    else:
        return False

    return True


def upload_new_asset_version(file_path=None, comment='Published new version with Solstice Tools', skip_saving=False):
    """
    Adds a new file to the Artella server
    :param file_path:
    :param comment:
    :param skip_saving: When we publish textures we do not want to save the maya scene
    """

    from solstice_pipeline.solstice_utils import solstice_maya_utils

    if not file_path:
        file_path = cmds.file(query=True, sceneName=True)
    if not file_path:
        sp.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    msg = 'Making new version for {}'.format(file_path)
    sp.logger.info(msg)
    sp.message(msg)
    if file_path is not None and file_path != '':
        valid_lock = lock_file(file_path=file_path)
        if not valid_lock:
            return False

        if not skip_saving:
            if cmds.file(query=True, modified=True):
                cmds.file(save=True, f=True)
            if solstice_maya_utils.file_has_student_line(filename=file_path):
                solstice_maya_utils.clean_student_line(filename=file_path)
                if solstice_maya_utils.file_has_student_line(filename=file_path):
                    sp.logger.error('After updating model path the Student License could not be fixed again!')
                    return False

        msg = 'Saving new file version on Artella Server: {}'.format(file_path)
        sp.logger.info(msg)
        sp.message(msg)
        if comment is None:
            result = cmds.promptDialog(title='Solstice Tools - Save New Version on Artella Server', message=msg, button=['Save', 'Cancel'], cancelButton='Cancel', dismissString='Cancel', scrollableField=True)
            if result == 'Save':
                comment = cmds.promptDialog(query=True, text=True)
            else:
                return False

        spigot = get_spigot_client()
        payload = dict()
        cms_uri = artella.getCmsUri(file_path)
        if not cms_uri.startswith('/'):
            cms_uri = '/' + cms_uri
        payload['cms_uri'] = cms_uri
        payload['comment'] = comment
        payload = json.dumps(payload)

        rsp = spigot.execute(command_action='do', command_name='upload', payload=payload)
        if isinstance(rsp, basestring) or type(rsp) == str:
            rsp = json.loads(rsp)

        if 'status' in rsp and 'meta' in rsp['status'] and rsp['status']['meta']['status'] != 'OK':
            sp.logger.info('Make new version response: {}'.format(rsp))
            msg = 'Failed to make new version of {}'.format(os.path.basename(file_path))
            cmds.confirmDialog(title='Solstice Tools - Failed to Make New Version', message=msg, button=['OK'])
            return False

        unlock_file(file_path=file_path)

    else:
        msg = 'The file has not been created yet'
        sp.logger.debug(msg)
        cmds.warning(msg)
        cmds.confirmDialog(title='Solstice Tools - Failed to Make New Version', message=msg, button=['OK'])

    return True


def publish_asset(asset_path, comment, selected_versions, version_name):
    """
    Publish a new version of the given asset
    :param asset_path:
    :param comment:
    :param selected_versions:
    :param version_name:
    """

    spigot = get_spigot_client()
    payload = dict()
    payload['cms_uri'] = '/' + artella.getCmsUri(asset_path) + '/' + version_name
    payload['comment'] = comment
    payload['selectedVersions'] = selected_versions
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='createRelease', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


def within_artella_scene():
    """
    Returns True if the current Maya scene corresponds to a Artella Maya scene
    :return: bool
    """

    current_scene = cmds.file(query=True, sn=True) or 'untitled'
    sp.logger.debug('Current scene name: {}'.format(current_scene))
    if 'artella' not in current_scene.lower():
        return False
    return True


def get_user_avatar(user_id):
    """
    Downloads from Artella the avatar of the given user id
    Only works if the user is loaded before to Artella
    :param user_id: str
    :return:
    """

    manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, artella_cms_url, 'default', 'default')
    auth = urllib2.HTTPBasicAuthHandler(manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    response = urllib2.urlopen('{0}/profile/{1}/avatarfull.img'.format(artella_cms_url, user_id))

    return response


def login_to_artella(user, password):
    """
    Login to Artella
    :param user: str, user name
    :param password: str, password
    :return:
    """

    # TODO: This always returns True, so its completely uselss :(

    manager = urllib2.HTTPPasswordMgrWithDefaultRealm()

    artella_web = 'https://www.artella.com/project/2252d6c8-407d-4419-a186-cf90760c9967'
    manager.add_password(None, artella_web, user, password)
    auth = urllib2.HTTPBasicAuthHandler(manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(artella_web)
    if response:
        if response.getcode() == 200:
            return True

    return False


def get_dependencies(file_path):
    """
    Returns a list with all the dependencies
    :param file_path: str
    :return: dict
    """

    if not file_path:
        file_path = cmds.file(query=True, sceneName=True)
    if not file_path:
        sp.logger.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    if file_path is not None and file_path != '':
        spigot = get_spigot_client()
        payload = dict()
        payload['cms_uri'] = artella.getCmsUri(file_path)
        payload = json.dumps(payload)

        rsp = spigot.execute(command_action='do', command_name='getDependencies', payload=payload)

        if isinstance(rsp, basestring):
            rsp = json.loads(rsp)
        sp.logger.debug(rsp)

        return rsp

    return None


try:
    import Artella as artella
except ImportError:
    try:
        load_artella_maya_plugin()
        update_artella_paths()
        import Artella as artella
    except Exception:
        sp.logger.debug('Artella is not set up properly in your computer!')


