#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains checks related with assets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json

import solstice.pipeline as sp
from solstice.pipeline.core import syncdialog
from solstice.pipeline.gui import messagehandler
from solstice.pipeline.tools.sanitycheck.checks import check
from solstice.pipeline.utils import artellautils as artella

from solstice.pipeline.tools.tagger import tagger

if sp.is_maya():
    from solstice.pipeline.utils import mayautils
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary


class AssetFileExists(check.SanityCheckTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        super(AssetFileExists, self).__init__(name='Check if Asset File exists', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._file_type = file_type
        self._status = status
        self._file_path = None
        self.set_check_text('Check if asset {0} {1} file exists'.format(status, file_type))

    def check(self):
        self._file_path = self._asset().get_asset_file(file_type=self._file_type, status=self._status)
        if self._file_path is None or not os.path.isfile(self._file_path):
            error_msg = 'File Path {} does not exists!\nCheck the nomenclature of the file please!'.format(self._file_path)
            sp.logger.error(error_msg)
            self.set_error_message(error_msg)
            return False

        return True

    def fix(self):
        if self._file_path:
            artella.synchronize_file(self._file_path)
        if self._file_path is None or not os.path.isfile(self._file_path):
            return False

        return True


class TexturesFolderSync(check.SanityCheckTask, object):
    def __init__(self, asset, auto_fix=False, parent=None):
        self._textures_path = list()
        super(TexturesFolderSync, self).__init__(name='Check textures folder sync', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self.set_check_text('Checking if asset {} has valid textures sync'.format(self._asset().name))

    def check(self):
        published_textures_info = self._asset().get_max_versions(status='published', categories=['textures'])['server']
        textures_version = published_textures_info['textures']
        if textures_version is None:
            error_msg = 'Textures Path folder has invalid textures or no textures at all!'.format(self._textures_path)
            sp.logger.error(error_msg)
            self.set_error_message(error_msg)
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


class AssetFileSync(check.SanityCheckTask, object):
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


class NotLockedAsset(check.SanityCheckTask, object):
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
            sp.logger.error(error_message)
            self.set_error_message(error_message)
            return False

        return True

    def fix(self):
        super(NotLockedAsset, self).fix()


class ValidPublishedTextures(check.SanityCheckTask, object):
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


class StudentLicenseCheck(check.SanityCheckTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        super(StudentLicenseCheck, self).__init__(name='Student License Check', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._status = status
        self._file_type = file_type
        self._file_path = None
        self.set_check_text('Check if Asset file has Student License')

    def check(self):

        if sp.is_maya():
            self._file_path = self._asset().get_asset_file(file_type=self._file_type, status=self._status)
            if self._file_path is None or not os.path.isfile(self._file_path):
                error_msg = 'File Path {} does not exists!'.format(self._file_path)
                sp.logger.error(error_msg)
                self.set_error_message(error_msg)
                return False

            return not mayautils.file_has_student_line(filename=self._file_path)

        return True

    def fix(self):
        if self._file_path is None or not os.path.isfile(self._file_path):
            return False

        if sp.is_maya():
            artella.lock_file(self._file_path)
            try:
                sp.logger.debug('Cleaning Student License from file: {}'.format(self._file_path))
                self._valid_check = mayautils.clean_student_line(filename=self._file_path)
                valid = super(StudentLicenseCheck, self).fix()
                if not valid:
                    sp.logger.warning('Impossible to fix Maya Student License Check')
                    artella.unlock_file(self._file_path)
                    return False
            except Exception as e:
                artella.unlock_file(self._file_path)
                return False

            artella.unlock_file(self._file_path)
            return True


class ValidTexturesPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidTexturesPath, self).__init__(name='Valid Textures Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid textures path')

    def check(self):
        if self._status == 'working':
            status = '__working__'
        else:
            return False

        textures_path = os.path.join(self._asset().asset_path, status, 'textures')
        self.write('Check if textures path {} is valid ...'.format(textures_path))
        if not os.path.exists(textures_path):
            self.write_error('Textures Path {} does not exists! Trying to sync ...'.format(textures_path))
            syncdialog.SolsticeSyncFile(files=[textures_path])
            if not os.path.exists(textures_path):
                self.write_error('Textures Path {} does not exists after sync!'.format(textures_path))
                return False

        self.write_ok('Textures Path | {} | is valid!\n\n'.format(status))

        return True

    def fix(self):
        return


class TexturesFolderIsEmpty(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(TexturesFolderIsEmpty, self).__init__(name='Valid Textures Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if textures folder has textures inside')

    def check(self):
        if self._status == 'working':
            status = '__working__'
        else:
            return False

        self.write('Checking if textures folder is not empty ...')

        textures_path = os.path.join(self._asset().asset_path, status, 'textures')
        if not os.path.exists(textures_path):
            self.write_error('Textures Path {} does not exists! Trying to sync ...'.format(textures_path))
            return False

        textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
        if len(textures) <= 0:
            self.write_error('Textures Folder {} has not textures.'.format(textures_path))
            return False

        self.write_ok('Textures Folder has textures inside it:')
        for i, txt in enumerate(textures):
            self.write('{}. {}'.format(i, os.path.basename(txt)))
        self.write('\n')

        return True

    def fix(self):
        return


class TextureFileSize(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(TextureFileSize, self).__init__(name='Valid Textures Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check texture file sizes')

    def check(self):
        if self._status == 'working':
            status = '__working__'
        else:
            return False

        self.write('Checking textures file sizes ...')

        textures_path = os.path.join(self._asset().asset_path, status, 'textures')
        if not os.path.exists(textures_path):
            self.write_error('Textures Path {} does not exists! Trying to sync ...'.format(textures_path))
            return False

        textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
        if len(textures) <= 0:
            self.write_error('Textures Folder {} has not textures.'.format(textures_path))
            return False

        for txt in textures:
            file_size = os.path.getsize(txt)
            if file_size <= 0:
                self.write_error('Texture {} has is invalid (size of 0).'.format(txt))
                return False

        self.write_ok('All Textures have valid size!')

        return True

    def fix(self):
        return


class TextureFilesLocked(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(TextureFilesLocked, self).__init__(name='Valid Textures Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if textures are locked by other user')

    def check(self):
        if self._status == 'working':
            status = '__working__'
        else:
            return False

        self.write('Checking textures file sizes ...')

        textures_path = os.path.join(self._asset().asset_path, status, 'textures')
        if not os.path.exists(textures_path):
            self.write_error('Textures Path {} does not exists! Trying to sync ...'.format(textures_path))
            return False

        textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
        if len(textures) <= 0:
            self.write_error('Textures Folder {} has not textures.'.format(textures_path))
            return False

        for txt in textures:
            file_size = os.path.getsize(txt)
            if file_size <= 0:
                self.write_error('Texture {} has is invalid (size of 0).'.format(txt))
                return False

        for txt in textures:
            can_unlock = artella.can_unlock(txt)
            if not can_unlock:
                self.write_error('Texture {} is locked by another Solstice team member or wokspace. Aborting publishing ...'.format(txt))
                return False

        self.write('Textures are not locked!')

        return True

    def fix(self):
        return


class ValidModelPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidModelPath, self).__init__(name='Valid Model Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid model path')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        self.write('Check if model path {} is valid ...'.format(model_path))
        if model_path is None or not os.path.isfile(model_path):
            self.write_error('Model Path {} is not valid!'.format(model_path))
            return False

        self.write('Model Path | {} | is valid!\n\n'.format(model_path))

        return True

    def fix(self):
        return


class ValidProxyPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidProxyPath, self).__init__(name='Valid Proxy Model Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid proxy model path')

    def check(self):
        if self._status != 'working':
            return False

        proxy_path = self._asset().get_asset_file(file_type='proxy', status=self._status)
        self.write('Check if proxy model path {} is valid ...'.format(proxy_path))
        if proxy_path is None or not os.path.isfile(proxy_path):
            self.write_error('Proxy Model Path {} is not valid!'.format(proxy_path))
            return False

        self.write('Proxy Model Path | {} | is valid!\n\n'.format(proxy_path))

        return True

    def fix(self):
        return


class ValidRigPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidRigPath, self).__init__(name='Valid Rig Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid rig path')

    def check(self):
        if self._status != 'working':
            return False

        rig_path = self._asset().get_asset_file(file_type='rig', status=self._status)
        self.write('Check if rig path {} is valid ...'.format(rig_path))
        if rig_path is None or not os.path.isfile(rig_path):
            self.write_error('Rig Path {} is not valid!'.format(rig_path))
            return False

        self.write('Rig Path | {} | is valid!\n\n'.format(rig_path))

        return True

    def fix(self):
        return


class ValidBuilderPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidBuilderPath, self).__init__(name='Valid Builder Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid builder path')

    def check(self):
        if self._status != 'working':
            return False

        builder_path = self._asset().get_asset_file(file_type='builder', status=self._status)
        self.write('Check if builder path {} is valid ...'.format(builder_path))
        if builder_path is None or not os.path.isfile(builder_path):
            self.write_error('Builder Path {} is not valid!'.format(builder_path))
            return False

        self.write('Rig Path | {} | is valid!\n\n'.format(builder_path))

        return True

    def fix(self):
        return


class ModelFileIsLocked(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ModelFileIsLocked, self).__init__(name='Model File is Locked', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if model file is locked by other user')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        self.write('Check if model file is already locked by other user or workspace ...')
        can_unlock = artella.can_unlock(model_path)
        if not can_unlock:
            self.write_error('Asset model file is locked by another Solstice team member or workspace.')
            return False

        return True

    def fix(self):
        return


class CleanModelUnknownNodes(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CleanModelUnknownNodes, self).__init__(name='Cleaning Model File', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('leaning unknown nodes from the model scene ... ')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        self.write('Opening model file in Maya ...')
        sp.dcc.open_file(model_path, force=True)

        # Clean unknown nodes and old plugins for the current scene
        self.write('Cleaning unknown nodes from the asset scene ...')
        unknown_nodes = sp.dcc.list_nodes(node_type='unknown')
        if unknown_nodes and type(unknown_nodes) == list:
            for i in unknown_nodes:
                if sp.dcc.object_exists(i):
                    if not sp.dcc.node_is_referenced(i):
                        self.write_ok('Removing {} item ...'.format(i))
                        sp.dcc.delete_object(i)
        unknown_nodes = sp.dcc.list_nodes(node_type='unknown')
        if unknown_nodes and type(unknown_nodes) == list:
            if len(unknown_nodes) > 0:
                self.write_error('Error while removing unknown nodes. Please contact TD!')
            else:
                self.write_ok('Unknown nodes removed successfully!')

        self.write('Cleaning old plugins nodes from the asset scene ...')
        old_plugins = sp.dcc.list_old_plugins()
        if old_plugins and type(old_plugins) == list:
            for plugin in old_plugins:
                self.write_ok('Removing {} old plugin ...'.format(plugin))
                sp.dcc.remove_old_plugin(plugin)
        old_plugins = sp.dcc.list_old_plugins()
        if old_plugins and type(old_plugins) == list:
            if len(old_plugins) > 0:
                self.write_error('Error while removing old plugins nodes. Please contact TD!')
            else:
                self.write_ok('Old Plugins nodes removed successfully!')

        return True

    def fix(self):
        return


class CheckModelMainGroup(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CheckModelMainGroup, self).__init__(name='Check Model main group', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking if model scene has a valid main group')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        model_main_group = '{}{}{}'.format(self._asset().name, sp.separator, sp.model_suffix)
        if sp.dcc.object_exists(model_main_group):
            objs = sp.dcc.list_nodes(node_name=model_main_group)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(model_main_group))
                return False
        else:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(model_main_group))
            return False
        self.write_ok('Asset main group is valid: {}'.format(model_main_group))

        return True

class CheckModelProxyMainGroup(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CheckModelProxyMainGroup, self).__init__(name='Check Proxy Model main group', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking if proxy model scene has a valid main group')

    def check(self):
        if self._status != 'working':
            return False

        proxy_path = self._asset().get_asset_file(file_type='proxy', status=self._status)
        if proxy_path is None or not os.path.isfile(proxy_path):
            return False

        self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        proxy_main_group = '{}{}{}'.format(self._asset().name, sp.separator, sp.proxy_suffix)
        if sp.dcc.object_exists(proxy_main_group):
            objs = sp.dcc.list_nodes(node_name=proxy_main_group)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(proxy_main_group))
                return False
        else:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(proxy_main_group))
            return False
        self.write_ok('Asset main group is valid: {}'.format(proxy_main_group))

        return True


class ModelHasNoShaders(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ModelHasNoShaders, self).__init__(name='Check model has no shaders', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking model has no shaders')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        # Check that model file has no shaders stored inside it
        shaders = sp.dcc.list_materials()
        invalid_shaders = list()
        for shader in shaders:
            if shader not in ['lambert1', 'particleCloud1']:
                invalid_shaders.append(shader)
        if len(invalid_shaders) > 0:
            self.write_error(
                'Model file has shaders stored in it: {}. Remove them before publishing the model file ...'.format(
                    invalid_shaders))
            return False
        self.write_ok('Model file has no shaders stored in it!')

        return True


class ProxyHasNoShaders(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ProxyHasNoShaders, self).__init__(name='Check proxy model has no shaders', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking proxy model has no shaders')

    def check(self):
        if self._status != 'working':
            return False

        proxy_path = self._asset().get_asset_file(file_type='proxy', status=self._status)
        if proxy_path is None or not os.path.isfile(proxy_path):
            return False

        # Check that model file has no shaders stored inside it
        shaders = sp.dcc.list_materials()
        invalid_shaders = list()
        for shader in shaders:
            if shader not in ['lambert1', 'particleCloud1']:
                invalid_shaders.append(shader)
        if len(invalid_shaders) > 0:
            self.write_error(
                'Proxy Model file has shaders stored in it: {}. Remove them before publishing the model file ...'.format(
                    invalid_shaders))
            return False
        self.write_ok('Proxy Model file has no shaders stored in it!')

        return True


class RigProxyHiresGroups(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(RigProxyHiresGroups, self).__init__(name='Check rig has valid proxy and hires groups', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking rig hires and proxy groups ... ')

    def check(self):
        if self._status != 'working':
            return False

        # rig_path = self._asset().get_asset_file(file_type='rig', status=self._status)
        # if rig_path is None or not os.path.isfile(rig_path):
        #     return False

        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                return False
        else:
            return False

        self.write('Checking if asset has valid proxy and hires groups')
        if not valid_obj:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            # self.write('Unlocking model file ...')
            # artella.unlock_file(rig_path)
            return False
        valid_proxy = False
        valid_hires = False
        proxy_grp = None
        hires_grp = None
        proxy_grp_name = '{}_proxy_grp'.format(self._asset().name)
        hires_grp_name = '{}_hires_grp'.format(self._asset().name)
        children = sp.dcc.list_relatives(node=valid_obj, all_hierarchy=True, full_path=True, relative_type='transform')
        if children:
            for child in children:
                child_name = child.split('|')[-1]
                if child_name == proxy_grp_name:
                    proxy_children = sp.dcc.list_relatives(node=child_name, all_hierarchy=True, relative_type='transform')
                    if len(proxy_children) > 0:
                        valid_proxy = True
                        if proxy_grp is None:
                            proxy_grp = child
                        else:
                            self.write_error('Multiple Proxy groups in the file. Please check it!')
                            return False
                    else:
                        self.write_error('Proxy group has no children!. Please check it!')
                        return False
                if child_name == hires_grp_name:
                    hires_children = sp.dcc.list_relatives(node=child_name, all_hierarchy=True, relative_type='transform')
                    if len(hires_children) > 0:
                        valid_hires = True
                        if hires_grp is None:
                            hires_grp = child
                        else:
                            self.write_error('Multiple Hires groups in the file. Please check it!')
                            return False

        if valid_proxy is True:
            self.write_ok('Proxy Group found successfully: {}'.format(proxy_grp))
        else:
            self.write_error(
                'Proxy Group not found! Group with name {} must exist in the model asset Maya file!'.format(
                    proxy_grp_name))
            return False
        if valid_hires is True:
            self.write_ok('Hires Group found successfully: {}'.format(hires_grp))
        else:
            self.write_error(
                'Hires Group not found! Group with name {} must exist in the model asset Maya file!'.format(
                    hires_grp_name))
            return False

        # Check if proxy group has valid proxy mesh stored
        if proxy_grp is None or not sp.dcc.object_exists(proxy_grp):
            self.write_error(
                'Proxy Group not found! Group with name {} must exist in the model asset Maya file!'.format(
                    hires_grp_name))
            return False

        proxy_mesh = None
        proxy_name = '{}_proxy'.format(self._asset().name)
        proxy_meshes = sp.dcc.list_relatives(node=proxy_grp, all_hierarchy=True, full_path=True, relative_type='transform')
        hires_meshes = sp.dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True, relative_type='transform')
        for mesh in proxy_meshes:
            child_name = mesh.split('|')[-1]
            if child_name == proxy_name:
                if proxy_mesh is None:
                    proxy_mesh = mesh
                else:
                    self.write_error('Multiple Proxy Meshes in the file. Please check it!')
                    return False

        if proxy_mesh is None or not sp.dcc.object_exists(proxy_mesh):
            self.write_error(
                'No valid Proxy Mesh in the file. Please check that proxy mesh follows nomenclature {}_proxy!'.format(
                    self._asset().name))
            return False

        if len(hires_meshes) <= 0:
            self.write_error('No Hires Meshes in the file. Please check it!')
            return False

        self.write_ok('Proxy and Hires groups have valid meshes stored inside them!')

        return True


class ValidTagDataNode(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidTagDataNode, self).__init__(name='Check if model file has valid TagData node', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking model has valid TagData node ... ')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                return False
        else:
            return False

        self.write('Checking if asset has a valid tag data node connected to its main group')
        if not valid_obj:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            return False

        valid_tag_data = False
        main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
        for connection in main_group_connections:
            attrs = sp.dcc.list_user_attributes(connection)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        if not valid_tag_data:
            self.write_warning('Main group has not a valid tag data node connected to. Creating it ...')
            try:
                sp.dcc.select_object(valid_obj)
                tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(self._asset().category)
                sp.dcc.clear_selection()
                self.write_ok('Tag Data Node created successfully!')
                self.write('Checking if Tag Data Node was created successfully ...')
                valid_tag_data = False
                main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
                for connection in main_group_connections:
                    attrs = sp.dcc.list_user_attributes(connection)
                    if attrs and type(attrs) == list:
                        for attr in attrs:
                            if attr == 'tag_type':
                                valid_tag_data = True
                if not valid_tag_data:
                    self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                    return False
            except Exception as e:
                self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                self.write_error(str(e))
                return False

            tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
            if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
                self.write_error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
                return False

        return True


class SetupTagDataNode(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(SetupTagDataNode, self).__init__(name='Check TagData connections ...', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Connect information to TagData ... ')

    def check(self):
        if self._status != 'working':
            return False

        model_path = self._asset().get_asset_file(file_type='model', status=self._status)
        if model_path is None or not os.path.isfile(model_path):
            return False

        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                return False
        else:
            return False

        tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
            self.write_error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        self.write('Connecting proxy group to tag data node')
        valid_connection = tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Proxy group connected to tag data node successfully!')
        else:
            self.write_error(
                'Error while connecting Proxy Group to tag data node!  Check Maya editor for more info about the error!')
            self.write('Unlocking model file ...')
            artella.unlock_file(model_path)
            return False

        # Connect hires group to tag data node
        self.write('Connection hires group to tag data node')
        valid_connection = tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Hires group connected to tag data node successfully!')
        else:
            self.write_error(
                'Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            self.write('Unlocking model file ...')
            artella.unlock_file(model_path)
            return False

        return True


class ValidShadingPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ValidShadingPath, self).__init__(name='Valid Shading Path', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if asset has valid shading path')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status=self._status)
        self.write('Check if shading path {} is valid ...'.format(shading_path))
        if shading_path is None or not os.path.isfile(shading_path):
            self.write_error('Shading Path {} is not valid!'.format(shading_path))
            return False

        self.write('Shading Path | {} | is valid!\n\n'.format(shading_path))

        return True

    def fix(self):
        return


class CleanShadingUnknownNodes(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CleanShadingUnknownNodes, self).__init__(name='Cleaning Shading File', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Cleaning unknown nodes from the model scene ... ')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status=self._status)
        if shading_path is None or not os.path.isfile(shading_path):
            return False

        self.write('Opening shading file in Maya ...')
        sp.dcc.open_file(shading_path, force=True)

        # Clean unknown nodes and old plugins for the current scene
        self.write('Cleaning unknown nodes from the asset scene ...')
        unknown_nodes = sp.dcc.list_nodes(node_type='unknown')
        if unknown_nodes and type(unknown_nodes) == list:
            for i in unknown_nodes:
                if sp.dcc.object_exists(i):
                    if not sp.dcc.node_is_referenced(i):
                        self.write_ok('Removing {} item ...'.format(i))
                        sp.dcc.delete_object(i)
        unknown_nodes = sp.dcc.list_nodes(node_type='unknown')
        if unknown_nodes and type(unknown_nodes) == list:
            if len(unknown_nodes) > 0:
                self.write_error('Error while removing unknown nodes. Please contact TD!')
            else:
                self.write_ok('Unknown nodes removed successfully!')

        self.write('Cleaning old plugins nodes from the asset scene ...')
        old_plugins = sp.dcc.list_old_plugins()
        if old_plugins and type(old_plugins) == list:
            for plugin in old_plugins:
                self.write_ok('Removing {} old plugin ...'.format(plugin))
                sp.dcc.remove_old_plugin(plugin)
        old_plugins = sp.dcc.list_old_plugins()
        if old_plugins and type(old_plugins) == list:
            if len(old_plugins) > 0:
                self.write_error('Error while removing old plugins nodes. Please contact TD!')
            else:
                self.write_ok('Old Plugins nodes removed successfully!')

        return True

    def fix(self):
        return


class ShadingFileIsLocked(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ShadingFileIsLocked, self).__init__(name='Shading File is Locked', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Check if shading file is locked by other user')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status=self._status)
        if shading_path is None or not os.path.isfile(shading_path):
            return False

        self.write('Check if shading file is already locked by other user or workspace ...')
        can_unlock = artella.can_unlock(shading_path)
        if not can_unlock:
            self.write_error('Asset shading file is locked by another Solstice team member or workspace.')
            return False

        return True

    def fix(self):
        return


class CheckShadingMainGroup(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CheckShadingMainGroup, self).__init__(name='Check Shading main group', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking if shading scene has a valid main group')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status=self._status)
        if shading_path is None or not os.path.isfile(shading_path):
            return False

        self.write('Checking if shading main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                return False
        else:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            return False
        self.write_ok('Asset main group is valid: {}'.format(self._asset().name))

        return True


class CheckShadingShaders(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(CheckShadingShaders, self).__init__(name='Check shadings in shading file', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking shaders validity')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status=self._status)
        if shading_path is None or not os.path.isfile(shading_path):
            return False

        self.write('Getting asset shaders from shading file ...')
        shaders = sp.dcc.list_materials()
        asset_shaders = list()
        for shader in shaders:
            if shader not in ['lambert1', 'particleCloud1']:
                asset_shaders.append(shader)
        if len(asset_shaders) > 0:
            self.write_ok('Valid shaders found on shading file: {}'.format(asset_shaders))
        else:
            self.write_error('Shading file has not valid shaders inside it! Aborting publishing ...')
            return False

        self.write('Checking that nomenclature of shaders and shading groups are valid')
        shader_types = sp.dcc.list_node_types('shader')
        for shader in asset_shaders:
            if shader in ['lambert1', 'particleCloud1']:
                continue
            if 'displacement' in shader or 'Displacement' in shader:
                continue
            if not shader.startswith(self._asset().name):
                self.write_error('Shader {} has not a valid nomenclature. Rename it with prefix {}'.format(shader, self._asset().name))
                return False
            shading_groups = sp.dcc.list_connections_of_type(node=shader, connection_type='shadingEngine')
            if not shading_groups or len(shading_groups) <= 0:
                self.write_warning('Shader {} has not a shading group connected to it!'.format(shader))
                continue
            if len(shading_groups) > 2:
                self.write_error(
                    'More than one shading groups found on shader {0} >> {1}. Aborting publishing ...'.format(shader,
                                                                                                              shading_groups))
                return False
            shading_group = shading_groups[0]
            connections = sp.dcc.list_source_connections(node=shading_group)
            if connections is not None:
                connected_shaders = list()
                for cnt in connections:
                    if sp.dcc.object_type(cnt) in shader_types:
                        connected_shaders.append(cnt)
                if len(connected_shaders) > 0:
                    target_name = sp.dcc.list_connections(node=shading_group, attribute_name='surfaceShader')[0]
                    if shading_group != '{}SG'.format(target_name, shader):
                        self.write_error(
                            'Shader invalid nomenclature: Target name: {} ---------- {} => {}'.format(target_name,
                                                                                                      shader,
                                                                                                      shading_group))
                        return False
            else:
                if shading_group != '{}_{}SG'.format(self._asset().name, shader):
                    self.write_error(
                        'Shading Group {0} does not follows a valid nomenclature. Rename it to {1}_{2}SG'.format(
                            shading_group, self._asset().name, shader))
                    return False
        self.write_ok('Shader {0} has a valid shading group: {1}'.format(shader, shading_group))
        self.write('Shading groups checked successfully!')

        return True


class UpdateTexturesPath(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='published', auto_fix=False, parent=None):
        super(UpdateTexturesPath, self).__init__(name='Updating textures path in shading file', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Updating textures paths validity')

    def check(self):

        import maya.cmds as cmds

        if self._status != 'published':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status='working')
        if not os.path.isfile(shading_path):
            return False

        solstice_var = os.path.normpath(os.environ['SOLSTICE_PROJECT'])
        solstice_full_id = os.path.normpath(sp.solstice_project_id_full)
        self.write('Updating textures paths ...')
        textures_updated = False
        current_textures_path = self._asset().get_asset_textures(force_sync=True)
        all_file_nodes = cmds.ls(et="file")
        for f in all_file_nodes:
            orig_texture_name = os.path.normpath(cmds.getAttr("%s.fileTextureName" % f))
            current_texture_path = orig_texture_name
            for txt in current_textures_path:
                texture_name = os.path.basename(current_texture_path)
                if texture_name in os.path.basename(txt):
                    if not os.path.normpath(txt) == os.path.normpath(current_texture_path):
                        current_texture_path = current_texture_path.replace(current_texture_path, txt)

            if current_texture_path.startswith('$ART_LOCAL_ROOT'):
                current_texture_path = current_texture_path.replace('$ART_LOCAL_ROOT', solstice_var)
            if current_texture_path.startswith(solstice_var):
                current_texture_path = current_texture_path.replace(solstice_var, '$SOLSTICE_PROJECT\\\\')
            else:
                if solstice_full_id in current_texture_path:
                    rep_str = current_texture_path.split(solstice_full_id)[0]+solstice_full_id
                    current_texture_path = current_texture_path.replace(rep_str, '$SOLSTICE_PROJECT')

            # current_texture_path = current_texture_path.replace('/', '\\')

            if orig_texture_name != current_texture_path:
                textures_updated = True
            if textures_updated:
                current_texture_path = current_texture_path.replace('\\', '/')
                self.write('>>>\n\t{0}'.format(os.path.normpath(cmds.getAttr("%s.fileTextureName" % f))))
                self.write_ok('\t{0}\n'.format(os.path.normpath(current_texture_path)))
                cmds.setAttr('{}.fileTextureName'.format(f), current_texture_path, type='string')

        if textures_updated:
            self.write_ok('Textures Path updated successfully!')
            messagehandler.MessageHandler().show_info_dialog('Textures updated. Make sure to submit shading file: {}'.format(shading_path))
        else:
            self.write('Textures paths are up-to-date')

        return True


class ExportShaderJSON(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None, publish=True):
        super(ExportShaderJSON, self).__init__(name='Exporting Shader JSON', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self._publish = publish
        self.set_check_text('Updating textures paths validity')

    def check(self):
        if self._status != 'working':
            return False

        shading_path = self._asset().get_asset_file(file_type='shading', status='working')
        if not os.path.isfile(shading_path):
            return False

        sp.dcc.open_file(shading_path, force=True)

        # Check that shading file has a main group with valid name
        self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error(
                    'Main group is not valid. Please change it manually to {}\n'.format(self._asset().name))
                return False
        else:
            self.write_error(
                'Main group is not valid. Please change it manually to {}\n'.format(self._asset().name))
            return False
        self.write_ok('Asset main group is valid: {}\n'.format(self._asset().name))

        # Check model file proxy and hires meshes
        if not valid_obj:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            return False

        shading_meshes = list()
        self.write('Getting meshes of shading file ...')
        xform_relatives = sp.dcc.list_relatives(node=valid_obj, all_hierarchy=True, full_path=True,
                                                relative_type='transform', shapes=False, intermediate_shapes=False)
        if xform_relatives:
            for obj in xform_relatives:
                if sp.dcc.object_exists(obj):
                    shapes = sp.dcc.list_shapes(node=obj, full_path=True, intermediate_shapes=False)
                    if shapes:
                        self.write('Found mesh on shading file: {}'.format(obj))
                        shading_meshes.append(obj)
        self.write_ok('Found {} meshes on shading file!'.format(len(shading_meshes)))

        self.write('Exporting Shaders JSON info file ...')
        info = shaderlibrary.ShaderLibrary.export_asset(asset=self._asset(), shading_meshes=shading_meshes, publish=self._publish)
        if info is None or not os.path.exists(info):
            self.write_error('Model Shader JSON file was not generated successfully. Please contact TD!')
            self.write('Unlocking shading file ...')
            return False
        self.write_ok('Asset shaders exported successfully!')
        self.write_ok('Model Shader JSON file: {}'.format(info))


class RenameShaders(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(RenameShaders, self).__init__(name='Renaming shaders ...', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Updating textures paths validity')

    def check(self):
        if self._status != 'working':
            return False

        if not sp.is_maya():
            sp.logger.warning('Rename shaders check is only available in Maya')
            return

        import maya.cmds as cmds

        shading_path = self._asset().get_asset_file(file_type='shading', status='working')
        if not os.path.isfile(shading_path):
            return False

        sp.dcc.open_file(shading_path, force=True)

        self.write('Retrieve scene shaders ...')

        def_mats = ['lambert1', 'particleCloud1']
        def_sgs = ['initialParticleSE', 'initialShadingGroup']

        mats = cmds.ls(mat=True)
        for mat in mats:
            if mat in def_mats:
                continue

            if not mat.startswith(self._asset().name):
                new_mat_name = '{}_{}'.format(self._asset().name, mat)
                if cmds.objExists(new_mat_name):
                    self.write_warning('Material {} already exists in scene. Rename it manually ...'.format(new_mat_name))
                    continue
                self.write_ok('Renaming material {} > {}'.format(mat, new_mat_name))
                cmds.rename(mat, new_mat_name)

        shaders = cmds.ls(type='shadingEngine')
        for sg in shaders:
            shd_mat = cmds.listConnections('{}.surfaceShader'.format(sg))
            if not shd_mat or len(shd_mat) <= 0:
                self.write_warning('No material connected to surface shader: {}!'.format(sg))
                continue
            if len(shd_mat) > 1:
                self.write_warning('Multiple materials: {} conntected to surface shader: {}!'.format(shd_mat, sg))
                continue
            shd_mat = shd_mat[0]
            if shd_mat in def_mats:
                continue
            new_sg_name = '{}SG'.format(shd_mat)
            if sg != new_sg_name:
                self.write_ok('Renaming surface shader {} > {}'.format(sg, new_sg_name))
                cmds.rename(sg, new_sg_name)

        mats = cmds.ls(mat=True)
        shaders = cmds.ls(type='shadingEngine')

        all_valid = True
        for mat in mats:
            if mat in def_mats:
                continue
            if not mat.startswith(self._asset().name):
                self.write_error('Material {} has not a valid nomenclature! It must starts with {}!'.format(mat, self._asset().name))
                all_valid = False
                continue

        for sg in shaders:
            if sg in def_sgs:
                continue
            if not sg.startswith(self._asset().name):
                self.write_error('Shader {} has not a valid nomenclature! It must starts with {}!'.format(sg, self._asset().name))
                all_valid = False
                continue
            if not sg.endswith('SG'):
                self.write_error('Shader {} has not a valid nomenclature! It must ends with SG!')
                all_valid = False
                continue

        if all_valid:
            self.write_ok('All materials and shaders have a valid nomenclature!')

        return all_valid


class ExportShaders(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None, publish=True):
        super(ExportShaders, self).__init__(name='Exporting shaders ...', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self._publish = publish
        self.set_check_text('Exporting shaders ...')

    def check(self):
        if self._status != 'working':
            return False

        if not sp.is_maya():
            sp.logger.warning('Rename shaders check is only available in Maya')
            return

        shading_path = self._asset().get_asset_file(file_type='shading', status='working')
        if not os.path.isfile(shading_path):
            return False

        self.write('Exporting Shaders files ...')
        exported_shaders = shaderlibrary.ShaderLibrary.export_asset_shaders(self._asset(), status=self._status, publish=self._publish)
        if exported_shaders:
            self.write_ok('Exported following shaders:')
            for sh in exported_shaders:
                self.write_ok(sh)
            return True

        return False


class CheckRigTag(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None, publish=True):
        super(CheckRigTag, self).__init__(name='Check model tag', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self._publish = publish
        self.set_check_text('Checking model tag ...')

    def check(self):
        if self._status != 'working':
            return False

        if not sp.is_maya():
            sp.logger.warning('Check Tag is only available in Maya')
            return

        rig_path = self._asset().get_asset_file(file_type='rig', status=self._status)
        if rig_path is None or not os.path.isfile(rig_path):
            return False
        if sp.dcc.scene_name() != rig_path:
            sp.dcc.open_file(rig_path)

        # Check that model file has a main group with valid name
        self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                return False

        # Check if main group has a valid tag node connected
        valid_tag_data = False
        main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
        for connection in main_group_connections:
            attrs = sp.dcc.list_user_attributes(connection)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        if not valid_tag_data:
            self.write_error('Main group has not a valid tag data node connected to it!')
            return False
        else:
            self.write_ok('Valid Tag Data node found for {}'.format(self._asset().name))

        return True


class UpdateTag(check.SanityCheckTask, object):
    def __init__(self, asset, file_type=None, log=None, status='working', auto_fix=False, parent=None, publish=True):
        super(UpdateTag, self).__init__(name='Update model tag', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self._publish = publish
        self._file_type = file_type
        self.set_check_text('Updating model tag ...')

    def check(self):
        if self._status != 'working':
            return False

        if not sp.is_maya():
            sp.logger.warning('Update Tag is only available in Maya')
            return

        if self._file_type:
            file_path = self._asset().get_asset_file(file_type=self._file_type, status=self._status)
            if file_path is None or not os.path.isfile(file_path):
                return False
            if sp.dcc.scene_name() != file_path:
                sp.dcc.open_file(file_path)
        else:
            file_path = sp.dcc.scene_name()

        # Check that model file has a main group with valid name
        self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
        valid_obj = None
        if sp.dcc.object_exists(self._asset().name):
            objs = sp.dcc.list_nodes(node_name=self._asset().name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                return False

        # Check if main group has a valid tag node connected
        valid_tag_data = False
        main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
        if main_group_connections:
            for connection in main_group_connections:
                attrs = sp.dcc.list_user_attributes(connection)
                if attrs and type(attrs) == list:
                    for attr in attrs:
                        if attr == 'tag_type':
                            valid_tag_data = True
                            break

        if not valid_tag_data:
            self.write_warning('Main group has not a valid tag data node connected to it. Creating it ...')
            try:
                sp.dcc.select_object(valid_obj)
                tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(self._asset().category)
                sp.dcc.clear_selection()
                self.write_ok('Tag Data Node created successfully!')
                self.write('Checking if Tag Data Node was created successfully ...')
                valid_tag_data = False
                main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
                for connection in main_group_connections:
                    attrs = sp.dcc.list_user_attributes(connection)
                    if attrs and type(attrs) == list:
                        for attr in attrs:
                            if attr == 'tag_type':
                                valid_tag_data = True
                if not valid_tag_data:
                    self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                    self.write('Unlocking model file ...')
                    artella.unlock_file(file_path)
                    return False
            except Exception as e:
                self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                self.write_error(str(e))
                return False

        tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
            self.write_error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        # Connect proxy group to tag data node
        self.write('Connecting proxy group to tag data node')
        valid_connection = tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Proxy group connected to tag data node successfully!')
        else:
            self.write_warning(
                'Error while connecting Proxy Group to tag data node! Check Maya editor for more info about the error!')

        # Connect hires group to tag data node
        self.write('Connection hires group to tag data node')
        valid_connection = tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Hires group connected to tag data node successfully!')
        else:
            self.write_warning(
                'Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            self.write('Unlocking model file ...')

        # Getting shaders info data
        shaders_file = shaderlibrary.ShaderLibrary.get_asset_shader_file_path(asset=self._asset())
        if not os.path.exists(shaders_file):
            self.write_error(
                'Shaders JSON file for asset {0} does not exists: {1}'.format(self._asset().name, shaders_file))
            self.write('Unlocking model file ...')
            artella.unlock_file(file_path)
            return False

        with open(shaders_file) as f:
            shader_data = json.load(f)
        if shader_data is None:
            self.write_error(
                'Shaders JSON file for asset {0} is not valid: {1}'.format(self._asset().name, shaders_file))
            self.write('Unlocking model file ...')
            artella.unlock_file(file_path)
            return False
        self.write_ok('Shaders JSON data loaded successfully!')

        self.write('Retrieving hires meshes ...')
        hires_grp = None
        hires_grp_name = '{}_hires_grp'.format(self._asset().name)
        if not sp.dcc.object_exists(hires_grp_name):
            hires_grp = self._asset().name

        children = sp.dcc.list_relatives(node=valid_obj, all_hierarchy=True, full_path=True, relative_type='transform')
        if children:
            for child in children:
                child_name = child.split('|')[-1]
                if child_name == hires_grp_name:
                    hires_children = sp.dcc.list_relatives(node=child_name, all_hierarchy=True,
                                                           relative_type='transform')
                    if len(hires_children) > 0:
                        if hires_grp is None:
                            hires_grp = child
                        else:
                            self.write_error('Multiple Hires groups in the file. Please check it!')
                            return False
        if not hires_grp:
            self.write_error('No hires group found ...')
            return False
        hires_meshes = sp.dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True, relative_type='transform')

        # Checking if shader data is valid
        self.write('Checking if shading meshes names and hires model meshes names are the same')
        check_meshes = dict()
        for shading_mesh, shading_group in shader_data.items():
            shading_name = shading_mesh.split('|')[-1]
            check_meshes[shading_mesh] = False
            for model_mesh in hires_meshes:
                mesh_name = model_mesh.split('|')[-1]
                if shading_name == mesh_name:
                    check_meshes[shading_mesh] = True

        valid_meshes = True
        for mesh_name, mesh_check in check_meshes.items():
            if mesh_check is False:
                self.write_error('Mesh {} not found in both model and shading file ...'.format(mesh_name))
                valid_meshes = False
        if not valid_meshes:
            self.write_error('Some shading meshes and model hires meshes are missed. Please contact TD!')
            return False
        else:
            self.write_ok('Shading Meshes and Model Hires meshes are valid!')

        # Create if necessary shaders attribute in model tag data node
        if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
            self.write_error('Tag data does not exists in the current scene!'.format(tag_data_node))
            return False

        attr_exists = sp.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
        if attr_exists:
            self.write('Unlocking shaders tag data attribute on tag data node: {}'.format(tag_data_node))
            sp.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')
        else:
            self.write('Creating shaders attribute on tag data node: {}'.format(tag_data_node))
            sp.dcc.add_string_attribute(node=tag_data_node, attribute_name='shaders')
            attr_exists = sp.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
            if not attr_exists:
                self.write_error('No Shaders attribute found on model tag data node: {}'.format(tag_data_node))
                return False
            else:
                self.write_ok('Shaders attribute created successfully on tag data node!')

        self.write('Storing shaders data into shaders tag data node attribute ...')
        sp.dcc.unlock_attribute(node=tag_data_node, attribute_name='shaders')
        sp.dcc.set_string_attribute_value(node=tag_data_node, attribute_name='shaders', attribute_value=shader_data)
        sp.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')
        self.write_ok('Shaders data added to model tag data node successfully!')

        return True







