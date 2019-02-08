#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_artella_classes.py
# by Tomas Poveda
# Utility Module that contains data classes for Artella information
#  with Artella
# ______________________________________________________________________
# ==================================================================="""

import os
import collections

import solstice_pipeline as sp


class ArtellaHeaderMetaData(object):
    def __init__(self, header_dict):

        self._container_uri = header_dict['container_uri'] if 'container_uri' in header_dict else None
        self._content_length = header_dict['content_length'] if 'content_length' in header_dict else 0
        self._date = header_dict['date'] if 'date' in header_dict else None
        self._status = header_dict['status'] if 'status' in header_dict else None
        self._content_type = header_dict['content_type'] if 'content_type' in header_dict else None
        self._type = header_dict['type']
        self._file_path = header_dict['file_path'] if 'file_path' in header_dict else None
        self._workspace_name = header_dict['workspace_name'] if 'workspace_name' in header_dict else None

    @property
    def container_uri(self):
        return self._container_uri

    @property
    def content_length(self):
        return self._content_length

    @property
    def date(self):
        return self._date

    @property
    def status(self):
        return self._status

    @property
    def content_type(self):
        return self._content_type

    @property
    def type(self):
        return self._type

    @property
    def file_path(self):
        return self._file_path

    @property
    def workspace_name(self):
        return self._workspace_name


class ArtellaAssetMetaData(object):
    def __init__(self, metadata_path, status_dict):

        self._path = metadata_path
        self._metadata_header = ArtellaHeaderMetaData(header_dict=status_dict['meta'])

        self.__latest = status_dict['data']['_latest']
        self._latest_ = status_dict['data']['latest']

        self._published_folders = dict()
        self._published_folders_all = dict()
        self._must_folders = sp.must_categories

        for f in self._must_folders:
            self._published_folders[f] = dict()
            self._published_folders_all[f] = dict()

        from solstice_utils import solstice_artella_utils as artella

        for name, data in status_dict['data'].items():
            if name == '_latest' or name == 'latest':
                continue

            # Before doing nothing, check if the published version is valid (has not been deleted from Artella manually)
            version_valid = True
            version_path = os.path.join(self._path, '__{0}__'.format(name))
            version_info = artella.get_status(version_path)
            if version_info:
                if isinstance(version_info, ArtellaHeaderMetaData):
                    version_valid = False
                else:
                    for n, d in version_info.references.items():
                        if d.maximum_version_deleted and d.deleted:
                            version_valid = False
                            break

            # Store all valid published folders
            for f in self._must_folders:
                if f in name:
                    version = sp.get_asset_version(name)[1]
                    if not version_valid:
                        self._published_folders_all[f][str(version)] = '__{0}__'.format(name)
                    else:
                        self._published_folders_all[f][str(version)] = '__{0}__'.format(name)
                        self._published_folders[f][str(version)] = '__{0}__'.format(name)

        # Sort all dictionaries by version number
        for f in self._must_folders:
            self._published_folders[f] = collections.OrderedDict(sorted(self._published_folders[f].items()))
            self._published_folders_all[f] = collections.OrderedDict(sorted(self._published_folders_all[f].items()))

    @property
    def path(self):
        return self._path

    @property
    def _latest(self):
        return self.__latest

    @property
    def latest(self):
        return self._latest_

    @property
    def published_models(self):
        return self._published_folders['model']

    @property
    def published_textures(self):
        return self._published_folders['textures']

    @property
    def published_shading(self):
        return self._published_folders['shading']

    def get_is_published(self):
        is_published = True
        for f in self._must_folders:
            must_dict = self._published_folders[f]
            if not must_dict:
                sp.logger.debug('Asset {0} is not published -> Folder "{1}" is not published yet!'.format(self._path, f))
                is_published = False
        return is_published

    def get_published_versions(self, all=False):
        if all:
            return self._published_folders_all
        else:
            return self._published_folders


class ArtellaReferencesMetaData(object):
    def __init__(self, ref_name, ref_path, ref_dict):
        self._name = ref_name.split('/')[-1]
        self._path = os.path.join(ref_path, ref_name)

        self._maximum_version_deleted = ref_dict['maximum_version_deleted'] if 'maximum_version_deleted' in ref_dict else False
        self._is_directory = ref_dict['is_directory'] if 'is_directory' in ref_dict else False
        self._deleted = ref_dict['deleted'] if 'deleted' in ref_dict else False
        self._local_version = ref_dict['local_version'] if 'local_version' in ref_dict else None
        self._view_version = ref_dict['view_version'] if 'view_version' in ref_dict else None
        self._relative_path = ref_dict['relative_path'] if 'relative_path' in ref_dict else None
        self._maximum_version = ref_dict['maximum_version'] if 'maximum_version' in ref_dict else None
        self._view_version_digest = ref_dict['view_version_digest'] if 'view_version_digest' in ref_dict else None
        self._locked = ref_dict['locked'] if 'locked' in ref_dict else False
        self._locked_view = ref_dict['locked_view'] if 'locked_view' in ref_dict else None
        self._locked_by = ref_dict['locked_by'] if 'locked_by' in ref_dict else None
        self._locked_by_display = ref_dict['lockedByDisplay'] if 'lockedByDisplay' in ref_dict else None

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def maximum_version_deleted(self):
        return self._maximum_version_deleted

    @property
    def is_directory(self):
        return self._is_directory

    @property
    def deleted(self):
        return self._deleted

    @property
    def local_version(self):
        return self._local_version

    @property
    def view_version(self):
        return self._view_version

    @property
    def relative_path(self):
        return self._relative_path

    @property
    def maximum_version(self):
        return self._maximum_version

    @property
    def view_version_digest(self):
        return self._view_version_digest

    @property
    def locked(self):
        return self._locked

    @property
    def locked_by(self):
        return self._locked_by

    @property
    def locked_view(self):
        return self._locked_view

    @property
    def locked_by_display(self):
        return self._locked_by_display

    def print_info(self):
        """
        Prints in logger the info of the current Artella object
        """

        sp.logger.debug('Name: {}'.format(self.name))
        sp.logger.debug('Path: {}'.format(self.path))
        sp.logger.debug('Maximum Version Deleted: {}'.format(self.maximum_version_deleted))
        sp.logger.debug('Is Directory: {}'.format(self.is_directory))
        sp.logger.debug('Is Deleted: {}'.format(self.deleted))
        sp.logger.debug('Local Version: {}'.format(self.local_version))
        sp.logger.debug('View Version: {}'.format(self.view_version))
        sp.logger.debug('Relative Path: {}'.format(self.relative_path))
        sp.logger.debug('Maximum Version: {}'.format(self.maximum_version))
        sp.logger.debug('View Version Digest: {}'.format(self.view_version_digest))
        sp.logger.debug('Locked: {}'.format(self.locked))
        sp.logger.debug('Locked By: {}'.format(self.locked_by))
        sp.logger.debug('Locked View: {}'.format(self.locked_view))
        sp.logger.debug('Locked By Display: {}'.format(self.locked_by_display))


class ArtellaDirectoryMetaData(object):
    def __init__(self, metadata_path, status_dict):

        self._path = metadata_path
        self._metadata_header = ArtellaHeaderMetaData(header_dict=status_dict['meta'])
        self._references = dict()

        for ref_name, ref_data in status_dict['data'].items():
            self._references[ref_name] = ArtellaReferencesMetaData(
                ref_name=ref_name,
                ref_path=metadata_path,
                ref_dict=ref_data)

    @property
    def path(self):
        return self._path

    @property
    def header(self):
        return self._metadata_header

    @property
    def references(self):
        return self._references

    def print_info(self):
        """
        Prints in logger the info of the current Artella object
        """

        sp.logger.debug('Path: {}'.format(self.path))
        sp.logger.debug('Header: {}'.format(self.header))
        sp.logger.debug('References: {}'.format(self.references))


class ArtellaAppMetaData(object):
    def __init__(self, cms_web_root, local_root, storage_id, token):
        """
        Class used to store data retrieve by getMetaData command
        :param client:
        """

        self._cms_web_root = cms_web_root
        self._local_root = local_root
        self._storage_id = storage_id
        self._token = token

    @property
    def cms_web_root(self):
        return self._cms_web_root

    @property
    def local_root(self):
        return self._local_root

    @property
    def storage_id(self):
        return self._storage_id

    @property
    def token(self):
        return self._token

    def update_local_root(self):
        """
        Updates the environment variable that stores the Artella Local Path
        NOTE: This is done by Artella plugin when is loaded, so we should not do it manually again
        :return:
        """

        sp.logger.debug('Updating Artella Local Root to {0}'.format(self._local_root))
        os.environ['ART_LOCAL_ROOT'] = self._local_root


class ArtellaFileVerionMetaData(object):
    def __init__(self, version_data):

        self._comment = None
        self._relative_dir = None
        self._name = None
        self._creator = None
        self._locked_by = None
        self._relative_path = None
        self._version = None
        self._creator_display = None
        self._date_created = None
        self._digest = None
        self._size = None

        if not version_data:
            return

        self._comment = version_data['comment']
        self._relative_path = version_data['relative_dir']
        self._name = version_data['name']
        self._creator = version_data['creator']
        self._locked_by = version_data['locked_by']
        self._relative_path = version_data['relative_path']
        self._version = version_data['version']
        self._creator_display = version_data['creatorDisplay']
        self._date_created = version_data['date_created']
        self._digest = version_data['digest']
        self._size = version_data['size']

    @property
    def comment(self):
        return self._comment

    @property
    def relative_dir(self):
        return self._relative_dir

    @property
    def name(self):
        return self._name

    @property
    def creator(self):
        return self._creator

    @property
    def locked_by(self):
        return self._locked_by

    @property
    def relative_path(self):
        return self._relative_path

    @property
    def version(self):
        return self._version

    @property
    def creator_display(self):
        return self._creator_display

    @property
    def date_created(self):
        return self._date_created

    @property
    def digest(self):
        return self._digest

    @property
    def size(self):
        return self._size


class ArtellaFileMetaData(object):
    def __init__(self, file_dict):

        self._name = None
        self._relative_path = None
        self._versions = dict()

        if not file_dict:
            return

        if file_dict['data']:
            for name, data in file_dict['data'].items():
                self._name = data['name']
                self._relative_path = data['relative_path']

                for version in data['versions']:
                    new_version = ArtellaFileVerionMetaData(version_data=version)
                    self._versions[str(new_version.version)] = new_version

                # Sort versions by key
                self._versions = sorted(self._versions.items())

    @property
    def name(self):
        return self._name

    @property
    def relative_path(self):
        return self._relative_path

    @property
    def versions(self):
        return self._versions
