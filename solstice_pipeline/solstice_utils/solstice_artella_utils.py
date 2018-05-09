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
import subprocess
import urllib2

import maya.cmds as cmds

import solstice_pipeline as sp
import solstice_maya_utils as utils
import solstice_artella_classes as classes

artella_maya_plugin_name = 'Artella.py'
artella_app_name = 'lifecycler'

spigot_client = None

# ---------------------------------------------------------------------------------------


def update_artella_paths():
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    artella_folder = get_artella_data_folder()
    for subdir, dirs, files in os.walk(artella_folder):
        if subdir not in sys.path:
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

    # TODO: This should not work in MAC, find a cross-platform way of doing this
    artella_folder = os.path.join(os.getenv('PROGRAMDATA'), 'Artella')
    artella_folder = [os.path.join(artella_folder, name) for name in os.listdir(artella_folder) if os.path.isdir(os.path.join(artella_folder, name)) and name != 'ui']
    if len(artella_folder) == 1:
        artella_folder = artella_folder[0]
    else:
        sp.logger.debug('Artella folder not found!')

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

    artella_folder = get_artella_data_folder()
    return os.path.join(get_artella_plugins_folder(), dcc)


def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    artella_folder = os.path.dirname(get_artella_data_folder())
    return os.path.join(artella_folder, artella_app_name)


def launch_artella_app():
    """
    Executes Artella App
    """

    # TODO: This should not work in MAC, find a cross-platform way of doing this
    if os.name == 'mac':
        artella_app_file = get_artella_app() + '.bundle'
    else:
        artella_app_file = get_artella_app() + '.exe'

    if os.path.isfile(artella_app_file):
        subprocess.call([artella_app_file])


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


def get_status(filepath, as_json=False):
    """
    Returns the status of  the given file path
    :param filepath: str
    :return: str
    """

    uri = get_cms_uri(filepath)

    spigot = get_spigot_client()
    rsp = spigot.execute(command_action='do', command_name='status', payload=uri)
    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

        # TODO: Print cannot be used because if we use threads Maya will crash, check if logger crash Maya
        # sp.logger.debug(rsp)

    if as_json:
        return rsp

    if 'data' in rsp:
        if '_latest'in rsp['data']:
            # if 'SEQ' not in rsp['meta']['container_uri']:
            status_metadata = classes.ArtellaAssetMetaData(metadata_path=filepath, status_dict=rsp)
            return status_metadata

        status_metadata = classes.ArtellaDirectoryMetaData(metadata_path=filepath, status_dict=rsp)
    else:
        status_metadata = classes.ArtellaHeaderMetaData(header_dict=rsp['meta'])

    return status_metadata

# return artella.getStatus(filepath)


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

    sp.logger.debug('Retrieved CMS uri: {0}'.format(cms_uri))
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

    uri = get_cms_uri(path)
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

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

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


def open_file_in_maya(file_path, maya_version=2017):
    """
    Open the given path in the given Maya version
    :param file_path: str
    :param maya_version: int
    """

    spigot = get_spigot_client()

    # Firt we try to open the app if its not launched
    payload = dict()
    payload['appName'] = "maya.{0}".format(str(maya_version))
    payload['parameter'] = "\"{0}\"".format(file_path)
    payload['wait'] = "60"
    payload = json.dumps(payload)
    rsp = spigot.execute(command_action='do', command_name='launchApp', payload=payload)
    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)
    sp.logger.debug(rsp)

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


def publish_asset(file_path, comment, selected_versions):
    """
    Publish a new version of the given asset
    :param file_path:
    :param comment:
    :param selected_versions:
    """

    spigot = get_spigot_client()
    payload = dict()
    payload['cms_uri'] = artella.getCmsUri(file_path)
    payload['comment'] = comment
    payload['selectedVersions'] = selected_versions
    payload = json.dumps(payload)

    rsp = spigot.execute(command_action='do', command_name='createRelease', payload=payload)

    if isinstance(rsp, basestring):
        rsp = json.loads(rsp)

    sp.logger.debug(rsp)
    return rsp


try:
    import Artella as artella
except ImportError:
    load_artella_maya_plugin()
    update_artella_paths()
    import Artella as artella
