#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetchecks.py
# by Tomas Poveda
# Module that contains checks related with assets
# ______________________________________________________________________
# ==================================================================="""

import os

import pipeline as sp
from pipeline.tools.sanitycheck.checks import check
from pipeline.utils import artellautils as artella
from pipeline.gui import syncdialog


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
            from pipeline.utils import mayautils
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
            from pipeline.utils import mayautils
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

        self.write('Textures Path | {} | is valid!\n\n'.format(status))

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

        self.write('Textures Folder has textures inside it:')
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

        self.write('All Textures have valid size!')

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


class ModelProxyHiresGroups(check.SanityCheckTask, object):
    def __init__(self, asset, log=None, status='working', auto_fix=False, parent=None):
        super(ModelProxyHiresGroups, self).__init__(name='Check model has valid proxy and hires groups', auto_fix=auto_fix, log=log, parent=parent)

        self._asset = asset
        self._status = status
        self.set_check_text('Checking model hires and proxy groups ... ')

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

        self.write('Checking if asset has valid proxy and hires groups')
        if not valid_obj:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            self.write('Unlocking model file ...')
            artella.unlock_file(model_path)
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
                from pipeline.tools.tagger import tagger
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

        from pipeline.tools.tagger import tagger

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