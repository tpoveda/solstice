#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetchecks.py
# by Tomas Poveda
# Module that contains checks related with assets
# ______________________________________________________________________
# ==================================================================="""

import os

import solstice_pipeline as sp
from solstice_pipeline.solstice_checks import solstice_check
from solstice_pipeline.solstice_utils import solstice_maya_utils
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella


class TexturesFolderSync(solstice_check.SanityCheckTask, object):
    def __init__(self, asset, auto_fix=False, parent=None):
        self._textures_path = list()
        super(TexturesFolderSync, self).__init__(name='Check textures folder sync', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self.set_check_text('Checking if asset {} has valid textures sync'.format(self._asset().name))

    def check(self):
        published_textures_info = self._asset().get_max_versions(status='published', categories=['textures'])['server']
        textures_version = published_textures_info['textures']
        if textures_version is None:
            return False

        self._textures_path.append(os.path.join(self._asset().asset_path, '__working__', 'textures'))

        for i in range(1, textures_version+1):
            textures_version = '{0:03}'.format(published_textures_info['textures'])
            self._textures_path.append(os.path.join(self._asset().asset_path, '__textures_v{0}__'.format(textures_version)))

        valid_paths = True
        for p in self._textures_path:
            if os.path.exists(p):
                if len(os.listdir(p)) <= 0:
                    valid_paths = False
            else:
                valid_paths = False

        return valid_paths

    def fix(self):
        valid_paths = True
        for p in self._textures_path:
            artella.synchronize_file(p)
            sp.register_asset(p)

            if os.path.exists(p):
                if len(os.listdir(p)) <= 0:
                    valid_paths = False
            else:
                valid_paths = False

        return valid_paths


class AssetFileSync(solstice_check.SanityCheckTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        self.paths_to_sync = list()
        super(AssetFileSync, self).__init__(name='Syncing {0} {0} file'.format(file_type, status), auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._file_type = file_type
        self._status = status
        self.set_check_text('Asset shading file syncing')

    def check(self):

        if self._status == 'all' or self._status == 'working':
            if self._file_type == 'all':
                self.paths_to_sync.append(os.path.join(self._asset()._asset_path, '__working__'))
            else:
                self.paths_to_sync.append(os.path.join(self._asset()._asset_path, '__working__', self._file_type))

        max_versions = self._asset().get_max_published_versions()
        for f, version_list in max_versions.items():
            if not version_list:
                continue
            version_type = version_list[1]
            if self._status == 'all' or self._status == 'published':
                if self._file_type != 'all':
                    if self._file_types in version_type:
                        self.paths_to_sync.append(os.path.join(self._asset()._asset_path, '{0}'.format(version_list[1])))
                else:
                    self.paths_to_sync.append(os.path.join(self._asset()._asset_path, '{0}'.format(version_list[1])))

        valid_paths = True
        for p in self.paths_to_sync:
            if os.path.exists(p):
                if len(os.listdir(p)) <= 0:
                    valid_paths = False
            else:
                valid_paths = False

        return valid_paths

    def fix(self):
        valid_paths = True
        for p in self.paths_to_sync:
            artella.synchronize_file(p)
            sp.register_asset(p)

            if os.path.exists(p):
                if len(os.listdir(p)) <= 0:
                    valid_paths = False
            else:
                valid_paths = False

        return valid_paths


class NotLockedAsset(solstice_check.SanityCheckTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        super(NotLockedAsset, self).__init__(name='Asset {0} {1} file is not locked'.format(status, file_type), auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._status = status
        self._file_type = file_type
        self.set_check_text('Check if asset file is not locked')

    def check(self):
        current_user_can_unlock = self._asset().is_locked(self._file_type, status=self._status)[1]
        if not current_user_can_unlock:
            error_message = 'Asset {0} | {1} {2} file is locked!'.format(self._asset().name, self._status, self._file_type)
            sp.logger.debug(error_message)
            self.set_error_message(error_message)
            return False

        return True

    def fix(self):
        super(NotLockedAsset, self).fix()


class ValidPublishedTextures(solstice_check.SanityCheckTask, object):
    def __init__(self, asset, auto_fix=False, parent=None):
        super(ValidPublishedTextures, self).__init__(name='Valid Published Textures Check', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self.set_check_text('Check if asset has valid textures published')

    def check(self):
        published_textures_info = self._asset().get_max_versions(status='published', categories=['textures'])['server']
        if not published_textures_info or published_textures_info['textures'] is None:
            error_message = 'Asset {} has not textures published yet! Before publishing shading files you need to publish textures!'.format(self._asset().name)
            sp.logger.debug(error_message)
            self.set_error_message(error_message)
            return False

        return True

    def fix(self):
        super(ValidPublishedTextures, self).fix()


class UpdateAssetTextures(solstice_check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(UpdateAssetTextures, self).__init__(name='Updating Texture Paths', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Update textures path to new version if necessary')

    def check(self):
        pass

    def fix(self):
        pass


class ModelAndShadingFileHasValidModels(solstice_check.SanityCheckTask, object):
    def __init__(self, auto_fix=False, parent=None):
        super(ModelAndShadingFileHasValidModels, self).__init__(name='Checking Model and Shading File', auto_fix=auto_fix, parent=parent)

        self.set_check_text('Check if model and shading files shares the same models')

    def check(self):
        pass

    def fix(self):
        pass


class StudentLicenseCheck(solstice_check.SanityCheckTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        super(StudentLicenseCheck, self).__init__(name='Student License Check', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._status = status
        self._file_type = file_type
        self._file_path = None
        self.set_check_text('Check if Asset file has Student License')

    def check(self):

        self._file_path = self._asset().get_asset_file(file_type=self._file_type, status=self._status)
        if self._file_path is None or not os.path.exists(self._file_path):
            return False

        return not solstice_maya_utils.file_has_student_line(filename=self._file_path)

    def fix(self):
        if self._file_path is None or not os.path.exists(self._file_path):
            return False

        artella.lock_asset(self._file_path)
        try:
            solstice_maya_utils.clean_student_line(filename=self._file_path)
            valid = super(StudentLicenseCheck, self).fix()
            if not valid:
                sp.logger.warning('Impossible to fix Maya Student License Check')
                return False
        except Exception as e:
            artella.unlock_asset(self._file_path)
            return False

        artella.unlock_asset(self._file_path)
        return True
