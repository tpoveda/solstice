#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_artella_classes.py
# by Tomas Poveda
# Utility Module thata contains data classes for Artella information
#  with Artella
# ______________________________________________________________________
# ==================================================================="""

import os
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

    @property
    def path(self):
        return self._path

    @property
    def _latest(self):
        return self.__latest

    @property
    def latest(self):
        return self._latest_


class ArtellaReferencesMetaData(object):
    def __init__(self, ref_name, ref_path, ref_dict):
        self._name = ref_name.split('/')[-1]
        self._path = os.path.join(ref_path, ref_name)

        self._is_directory = ref_dict['is_directory'] if 'is_directory' in ref_dict else False
        self._maximum_version = ref_dict['maximum_version'] if 'maximum_version' in ref_dict else None
        self._relative_path = ref_dict['relative_path'] if 'relative_path' in ref_dict else None

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def is_directory(self):
        return self._is_directory


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


class ArtellaFileStatus(object):
    def __init__(self):
        pass