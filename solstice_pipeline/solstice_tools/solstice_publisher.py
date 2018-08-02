#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_publisher.py
# by Tomas Poveda
# Tool that is used to publish assets and sequences
# ______________________________________________________________________
# ==================================================================="""

import os
import re
import weakref
import traceback
from shutil import copyfile

import maya.cmds as cmds

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_dialog, solstice_splitters, solstice_spinner, solstice_console, solstice_sync_dialog
from solstice_pipeline.solstice_utils import solstice_qt_utils, solstice_maya_utils
from solstice_pipeline.solstice_utils import solstice_image as img
from solstice_pipeline.solstice_utils import solstice_python_utils as python
from solstice_pipeline.solstice_utils import solstice_artella_utils as artella
from solstice_pipeline.solstice_checks import solstice_validators
from solstice_pipeline.solstice_tasks import solstice_taskgroups, solstice_task

from resources import solstice_resource


class PublishTexturesTask(solstice_task.Task, object):
    def __init__(self, asset, new_version, comment='Published textures with Solstice Publisher', auto_run=False, parent=None):
        super(PublishTexturesTask, self).__init__(name='PublishTextures', auto_run=auto_run, parent=parent)

        self._asset = asset
        self._comment = comment
        self._new_version = new_version
        self.set_task_text('Publishing Textures ...')

    def run(self):

        self.write_ok('>>> PUBLISH TEXTURES LOG')
        self.write_ok('------------------------------------')

        # Do initial validation
        self.write('Doing textures initial validation ...')
        check = solstice_validators.TexturesValidator(asset=self._asset)
        check.check()
        if not check.is_valid():
            return False

        # Check if textures path is valid
        textures_path = os.path.join(self._asset().asset_path, '__working__', 'textures')
        self.write('Check if textures path {} is valid ...'.format(textures_path))
        if not os.path.exists(textures_path):
            self.write_error('Textures Path {} does not exists! Trying to sync ...'.format(textures_path))
            solstice_sync_dialog.SolsticeSyncFile(files=[textures_path])
            if not os.path.exists(textures_path):
                self.write_error('Textures Path {} does not exists after sync! Aborting textures publishing ...'.format(textures_path))
                return False

        # Check if there are folders inside textures folder
        self.write('Checking if textures folder is not empty ...')
        textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
        if len(textures) <= 0:
            self.write_error('Textures Folder {} has not textures. Aborting publishing ...'.format(textures_path))
            return False

        # Check that texture size is not zero
        self.write('Checking textures file sizes ...')
        for txt in textures:
            file_size = os.path.getsize(txt)
            if file_size <= 0:
                self.write_error('Texture {} has is invalid (size of 0). Aborting publishing ...'.format(txt))
                return False

        # Check if textures can be unlocked
        self.write('Check if textures are locked by other user or workspace ...')
        for txt in textures:
            can_unlock = artella.can_unlock(txt)
            if not can_unlock:
                self.write_error('Texture {} is locked by another Solstice team member or wokspace. Aborting publishing ...'.format(txt))
                return False

        # Lock all textures
        self.write('Locking textures files ...')
        for txt in textures:
            valid_lock = artella.lock_file(txt, force=True)
            if not valid_lock:
                self.write_error('Impossible to lock texture file {}. Maybe it is locked by other user!'.format(txt))
                return False

        try:
            self.write('Getting textures versions to publish ...')
            selected_versions = dict()
            for txt in textures:
                status = artella.get_status(txt)
                if status:
                    if status.references:
                        for ref, ref_data in status.references.items():
                            selected_versions[ref_data.relative_path] = ref_data.maximum_version

            result = solstice_qt_utils.show_question(None, 'Publishing textures {0}'.format(textures_path), 'Textures validated successfully! Do you want to continue with the publish process?')
            published_done = False
            if result == QMessageBox.Yes:
                version_name = '__textures_v{}__'.format(self._new_version)
                artella.publish_asset(asset_path=self._asset().asset_path, comment=self._comment, selected_versions=selected_versions, version_name=version_name)

                # We sync the new file
                new_sync_file = os.path.join(self._asset().asset_path, version_name)
                if not os.path.exists(new_sync_file):
                    solstice_sync_dialog.SolsticeSyncFile(files=[new_sync_file]).sync()
                if not os.path.exists(new_sync_file):
                    self.write_error('Impossible to sync the new published textures. Do it manually later please!')
                published_done = True

            # After publishing if we unlock the textures
            self.write('Unlocking texture files ...')
            for txt in textures:
                valid_unlock = artella.unlock_file(txt, force=True)
                if not valid_unlock:
                    self.write_error('Impossible to unlock texture file {}. Maybe it is locked by other user!'.format(txt))
                    return False

            if published_done:
                self.write_ok('Publishing textures process completed successfully!')
            else:
                self.write_error('Publishing textures process has been aborted by user!')

            self.write_ok('------------------------------------')
            self.write_ok('TEXTURES PUBLISHED SUCCESSFULLY!')
            self.write_ok('------------------------------------\n\n')
            self.write('\n')

            return published_done
        except Exception as e:
            self.write_error('Error while publishing textures files. Reverting process ...')
            sp.logger.error(str(e))
            self.write('Unlocking texture files ...')
            for txt in textures:
                valid_unlock = artella.unlock_file(txt)
                if not valid_unlock:
                    self.write_error(
                        'Impossible to unlock texture file {}. Maybe it is locked by other user!'.format(txt))
                    return False
            return False


class PublishModelTask(solstice_task.Task, object):
    def __init__(self, asset, new_version, comment='Published model with Solstice Publisher', auto_run=False, parent=None):
        super(PublishModelTask, self).__init__(name='PublishModel', auto_run=auto_run, parent=parent)

        self._asset = asset
        self._comment = comment
        self._new_version = new_version
        self.set_task_text('Publishing Model ...')

    def run(self):

        from solstice_pipeline.solstice_tools import solstice_tagger

        self.write_ok('>>> PUBLISH MODEL LOG')
        self.write_ok('------------------------------------')

        # Do initial validation
        self.write('Doing model initial validation ...')
        check = solstice_validators.ModelValidator(asset=self._asset)
        check.check()
        if not check.is_valid():
            self.write_error('Fail during initial validation ...')
            return False

        # Check if model path is valid
        model_path = self._asset().get_asset_file(file_type='model', status='working')
        self.write('Check if model path {} is valid ...'.format(model_path))
        if model_path is None or not os.path.isfile(model_path):
            self.write_error('Model Path {} is not vaild!'.format(model_path))
            return False

        # Check if model file can be unlocked
        self.write('Check if model file is already locked by other user or workspace ...')
        can_unlock = artella.can_unlock(model_path)
        if not can_unlock:
            self.write_error('Asset model file is locked by another Solstice team member or wokspace. Aborting publishing ...')
            return False

        # Lock model file
        self.write('Locking model file ...')
        valid_lock = artella.lock_file(model_path, force=True)
        if not valid_lock:
            self.write_error('Impossible to lock file {}. Maybe it is locked by other user!'.format(model_path))
            return False

        try:
            # Open model file scene
            self.write('Opening model file in Maya ...')
            cmds.file(model_path, o=True, f=True)

            # Clean unknown nodes and old plugins for the current scene
            self.write('Cleaning unknown nodes from the asset scene ...')
            unknown_nodes = cmds.ls(type='unknown')
            if unknown_nodes and type(unknown_nodes) == list:
                for i in unknown_nodes:
                    if cmds.objExists(i):
                        if not cmds.referenceQuery(i, isNodeReferenced=True):
                            self.write_ok('Removing {} item ...'.format(i))
                            cmds.delete(i)
            unknown_nodes = cmds.ls(type='unknown')
            if unknown_nodes and type(unknown_nodes) == list:
                if len(unknown_nodes) > 0:
                    self.write_error('Error while removing unknown nodes. Please contact TD!')
                else:
                    self.write_ok('Unknown nodes removed successfully!')

            self.write('Cleaning old plugins nodes from the asset scene ...')
            old_plugins = cmds.unknownPlugin(query=True, list=True)
            if old_plugins and type(old_plugins) == list:
                for plugin in old_plugins:
                    self.write_ok('Removing {} old plugin ...'.format(plugin))
                    cmds.unknownPlugin(plugin, remove=True)
            old_plugins = cmds.unknownPlugin(query=True, list=True)
            if old_plugins and type(old_plugins) == list:
                if len(old_plugins) > 0:
                    self.write_error('Error while removing old plugins nodes. Please contact TD!')
                else:
                    self.write_ok('Old Plugins nodes removed successfully!')

            # Check that model file has a main group with valid name
            self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
            valid_obj = None
            if cmds.objExists(self._asset().name):
                objs = cmds.ls(self._asset().name)
                for obj in objs:
                    parent = cmds.listRelatives(obj, parent=True)
                    if parent is None:
                        valid_obj = obj
                if not valid_obj:
                    self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                    self.write('Unlocking model file ...')
                    artella.unlock_file(model_path)
                    return False
            else:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False
            self.write_ok('Asset main group is valid: {}'.format(self._asset().name))

            # Check that model file has a valid proxy and hires group
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
            children = cmds.listRelatives(valid_obj, allDescendents=True, type='transform', fullPath=True)
            if children:
                for child in children:
                    child_name = child.split('|')[-1]
                    if child_name == proxy_grp_name:
                        proxy_children = cmds.listRelatives(child_name, allDescendents=True, type='transform')
                        if len(proxy_children) > 0:
                            valid_proxy = True
                            if proxy_grp is None:
                                proxy_grp = child
                            else:
                                self.write_error('Multiple Proxy groups in the file. Please check it!')
                                self.write('Unlocking model file ...')
                                artella.unlock_file(model_path)
                                return False
                        else:
                            self.write_error('Proxy group has no children!. Please check it!')
                            self.write('Unlocking model file ...')
                            artella.unlock_file(model_path)
                            return False
                    if child_name == hires_grp_name:
                        hires_children = cmds.listRelatives(child_name, allDescendents=True, type='transform')
                        if len(hires_children) > 0:
                            valid_hires = True
                            if hires_grp is None:
                                hires_grp = child
                            else:
                                self.write_error('Multiple Hires groups in the file. Please check it!')
                                self.write('Unlocking model file ...')
                                artella.unlock_file(model_path)
                                return False

            if valid_proxy is True:
                self.write_ok('Proxy Group found successfully: {}'.format(proxy_grp))
            else:
                self.write_error('Proxy Group not found! Group with name {} must exist in the model asset Maya file!'.format(proxy_grp_name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False
            if valid_hires is True:
                self.write_ok('Hires Group found successfully: {}'.format(hires_grp))
            else:
                self.write_error('Hires Group not found! Group with name {} must exist in the model asset Maya file!'.format(hires_grp_name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False

            # Check if proxy group has valid proxy mesh stored
            if proxy_grp is None or not cmds.objExists(proxy_grp):
                self.write_error('Proxy Group not found! Group with name {} must exist in the model asset Maya file!'.format(hires_grp_name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False

            proxy_mesh = None
            proxy_name = '{}_proxy'.format(self._asset().name)
            proxy_meshes = cmds.listRelatives(proxy_grp, allDescendents=True, type='transform', fullPath=True)
            hires_meshes = cmds.listRelatives(hires_grp, allDescendents=True, type='transform', fullPath=True)
            for mesh in proxy_meshes:
                child_name = mesh.split('|')[-1]
                if child_name == proxy_name:
                    if proxy_mesh is None:
                        proxy_mesh = mesh
                    else:
                        self.write_error('Multiple Proxy Meshes in the file. Please check it!')
                        self.write('Unlocking model file ...')
                        artella.unlock_file(model_path)
                        return False

            if proxy_mesh is None or not cmds.objExists(proxy_mesh):
                self.write_error('No valid Proxy Mesh in the file. Please check that proxy mesh follows nomenclature {}_proxy!'.format(self._asset().name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False

            if len(hires_meshes) <= 0:
                self.write_error('No Hires Meshes in the file. Please check it!')
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False

            self.write_ok('Proxy and Hires groups have valid meshes stored inside them!')

            # ============================================================================================================

            # Check if main group has a valid tag node connected
            self.write('Checking if asset has a valid tag data node connected to its main group')
            if not valid_obj:
                self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
                self.write('Unlocking model file ...')
                artella.unlock_file(model_path)
                return False

            valid_tag_data = False
            main_group_connections = cmds.listConnections(valid_obj, source=True)
            for connection in main_group_connections:
                attrs = cmds.listAttr(connection, userDefined=True)
                if attrs and type(attrs) == list:
                    for attr in attrs:
                        if attr == 'tag_type':
                            valid_tag_data = True
                            break

            if not valid_tag_data:
                self.write_error('Main group has not a valid tag data node connected to. Creating it ...')
                try:
                    from solstice_pipeline.solstice_tools import solstice_tagger
                    cmds.select(valid_obj)
                    solstice_tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(self._asset().category)
                    cmds.select(clear=True)
                    self.write_ok('Tag Data Node created successfully!')
                    self.write('Checking if Tag Data Node was created successfully ...')
                    valid_tag_data = False
                    main_group_connections = cmds.listConnections(valid_obj, source=True)
                    for connection in main_group_connections:
                        attrs = cmds.listAttr(connection, userDefined=True)
                        if attrs and type(attrs) == list:
                            for attr in attrs:
                                if attr == 'tag_type':
                                    valid_tag_data = True
                    if not valid_tag_data:
                        self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                        self.write('Unlocking model file ...')
                        artella.unlock_file(model_path)
                        return False
                except Exception as e:
                    self.write_error('Impossible to create tag data node. Please contact TD team to fix this ...')
                    self.write_error(str(e))
                    return False
        except Exception as e:
            self.write_error('Error while publishing model file. Reverting process ...')
            sp.logger.error(str(e))
            self.write('Unlocking model file ...')
            artella.unlock_file(model_path)
            return False

        tag_data_node = solstice_tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not cmds.objExists(tag_data_node):
            self.write_error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        # Connect proxy group to tag data node
        self.write('Connecting proxy group to tag data node')
        valid_connection = solstice_tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Proxy group connected to tag data node successfully!')
        else:
            self.write_error('Error while connecting Proxy Group to tag data node!  Check Maya editor for more info about the error!')
            return False

        # Connect hires group to tag data node
        self.write('Connection hires group to tag data node')
        valid_connection = solstice_tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if valid_connection:
            self.write_ok('Hires group connected to tag data node successfully!')
        else:
            self.write_error('Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            return False

        self.write('Saving change to model file ...')
        if cmds.file(query=True, modified=True):
            cmds.file(save=True, f=True)

        self.write('Check if we need to clean Student License again ...')
        if solstice_maya_utils.file_has_student_line(filename=model_path):
            solstice_maya_utils.clean_student_line(filename=model_path)
            if solstice_maya_utils.file_has_student_line(filename=model_path):
                self.write_error('After updating model path the Student License could not be fixed again!')
                return False

        self.write('Getting model file version to publish ...')
        selected_versions = dict()
        status = artella.get_status(model_path)
        if status and hasattr(status, 'references'):
            if status.references:
                for ref, ref_data in status.references.items():
                    selected_versions[ref] = ref_data.maximum_version
        if not selected_versions:
            self.write_error('No model file version to publish. Aborting publishing ...')
            return False

        result = solstice_qt_utils.show_question(None, 'Publishing file {0}'.format(model_path), 'File validated successfully! Do you want to continue with the publish process?')
        published_done = False
        if result == QMessageBox.Yes:
            version_name = '__model_v{}__'.format(self._new_version)
            artella.publish_asset(asset_path=self._asset().asset_path, comment=self._comment, selected_versions=selected_versions, version_name=version_name)

            # We sync the new file
            new_sync_file = os.path.join(self._asset().asset_path, version_name)
            if not os.path.exists(new_sync_file):
                solstice_sync_dialog.SolsticeSyncFile(files=[new_sync_file]).sync()
            if not os.path.exists(new_sync_file):
                self.write_error('Impossible to sync the new published model. Do it manually later please!')
            published_done = True

        # After publishing it we unlock the model file
        self.write('Unlocking model file ...')
        artella.unlock_file(model_path)

        if published_done:
            self.write_ok('Publishing model process completed successfully!')
            self.write_ok('------------------------------------')
            self.write_ok('MODEL PUBLISHED SUCCESSFULLY!')
            self.write_ok('------------------------------------\n\n')
            self.write('\n')
        else:
            self.write_error('Publishing model process has been aborted by the user!')

        return published_done


class PublishShadingTask(solstice_task.Task, object):
    def __init__(self, asset, new_version, comment='Published shading with Solstice Publisher', auto_run=False, parent=None):
        super(PublishShadingTask, self).__init__(name='PublishShading', auto_run=auto_run, parent=parent)

        self._asset = asset
        self._comment = comment
        self._new_version = new_version
        self.set_task_text('Publishing Shading ...')

    def run(self):

        from solstice_pipeline.solstice_tools import solstice_tagger

        self.write_ok('>>> PUBLISH SHADING LOG')
        self.write_ok('------------------------------------')

        # Do initial validation
        check = solstice_validators.ShadingValidator(asset=self._asset)
        check.check()
        if not check.is_valid():
            return False

        # Check if model and shading paths are valid
        model_path = self._asset().get_asset_file(file_type='model', status='working')
        self.write('Check if model path {} is valid ...'.format(model_path))
        self._asset().sync(sync_type='model', status='working')
        if model_path is None or not os.path.isfile(model_path):
            self.write_error('Model Path {} is not vaild!'.format(model_path))
            return False
        shading_path = self._asset().get_asset_file(file_type='shading', status='working')
        self.write('Check if shading path {} is valid ...'.format(shading_path))
        if shading_path is None or not os.path.isfile(shading_path):
            self.write_error('Asset shading file does not exists!')
            return False

        # Check shading file can be unlocked
        self.write('Check if shading file is already locked by other user or workspace ...')
        can_unlock = artella.can_unlock(shading_path)
        if not can_unlock:
            self.write_error('Asset shading file is locked by another Solstice team member or wokspace. Aborting publishing ...')
            return False

        # Check if files have a valid main group
        valid_obj = None
        for file_path, file_type in zip([model_path, shading_path], ['model', 'shading']):
            self.write('Checking if asset {0} file main group has a valid nomenclature: {1}'.format(file_type, self._asset().name))
            cmds.file(file_path, o=True, f=True)
            if cmds.objExists(self._asset().name):
                objs = cmds.ls(self._asset().name)
                for obj in objs:
                    parent = cmds.listRelatives(obj, parent=True)
                    if parent is None:
                        valid_obj = obj
                if not valid_obj:
                    self.write_error('Asset {0} file main group is not valid. Please change it manually to {1}'.format(file_type, self._asset().name))
                    return False
            else:
                self.write_error('Asset {0} file main group is not valid. Please change it manually to {1}'.format(file_type,self._asset().name))
                return False
            self.write_ok('Asset {0} main group is valid: {1}'.format(file_type, self._asset().name))

        # Sync last working version texture files
        self.write('Syncing current published textures files of asset {}\n'.format(self._asset().name))
        self._asset().sync(sync_type='textures', status='published')

        # Create backup of the file
        self.write('Creating Shading backup file')
        filename, extension = os.path.splitext(shading_path)
        backup_file = filename + '_BACKUP' + extension
        copyfile(shading_path, backup_file)
        self.write_ok('SHADING BACKUP: {}'.format(backup_file))

        # Check model file proxy and hires meshes
        if not valid_obj:
            self.write_error('Main group is not valid. Please change it manually to {}'.format(self._asset().name))
            return False

        model_proxy_group = None
        model_hires_group = None
        model_proxy_mesh = None
        model_hires_meshes = list()
        self.write('Opening model file in Maya ...')
        cmds.file(model_path, o=True, f=True)
        tag_data_node = solstice_tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not cmds.objExists(tag_data_node):
            self.write_error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        self.write('Getting proxy mesh from tag data node ...')
        attr_exists = cmds.attributeQuery('proxy', node=tag_data_node, exists=True)
        if not attr_exists:
            self.write_error('Model Tag Data node has not a proxy connection. Model file is not set up yet. Please contact TD!')
            return False
        model_proxy_group = cmds.listConnections(tag_data_node + '.proxy')
        if model_proxy_group:
            model_proxy_group = model_proxy_group[0]
        if model_proxy_group is not None and cmds.objExists(model_proxy_group):
            for obj in cmds.listRelatives(model_proxy_group, children=True, type='transform', shapes=False, noIntermediate=True, fullPath=True):
                if cmds.objExists(obj):
                    shapes = cmds.listRelatives(obj, shapes=True)
                    if shapes:
                        if model_proxy_mesh is None:
                            model_proxy_mesh = obj
                        else:
                            self.write_error('Multiple proxy meshes in model file. Asset only can have one proxy mesh! Please contact TD!')
                            return False
        if model_proxy_mesh is None or not cmds.objExists(model_proxy_mesh):
            self.write_error('Proxy mesh not found in model file! Please contact TD!')
            return False
        self.write_ok('Proxy Mesh found on model file: {}'.format(model_proxy_mesh))

        self.write('Getting hiresh meshes from tag data node ...')
        attr_exists = cmds.attributeQuery('hires', node=tag_data_node, exists=True)
        if not attr_exists:
            self.write_error('Model Tag Data has not a hires connection. Model file is not set up yet. Please contact TD team!')
            return False
        model_hires_group = cmds.listConnections(tag_data_node + '.hires')
        if model_hires_group:
            model_hires_group = model_hires_group[0]
        if model_hires_group is not None and cmds.objExists(model_hires_group):
            for obj in cmds.listRelatives(model_hires_group, children=True, type='transform', shapes=False, noIntermediate=True, fullPath=True):
                if cmds.objExists(obj):
                    shapes = cmds.listRelatives(obj, shapes=True)
                    if shapes:
                        self.write('Found hires mesh on model file: {}'.format(obj))
                        model_hires_meshes.append(obj)
        if len(model_hires_meshes) <= 0:
            self.write_error('Hires meshes not found on model file!')
            return False
        self.write_ok('Found {} hires meshes on model file!'.format(len(model_hires_meshes)))

        # Lock shading file
        self.write('Locking shading file ...')
        valid_lock = artella.lock_file(shading_path, force=True)
        if not valid_lock:
            self.write_error('Impossible to lock file {}. Maybe it is locked by other user!'.format(shading_path))
            return False

        try:
            current_textures_path = self._asset().get_asset_textures()
            with open(shading_path, 'r') as f:
                data = f.read()
                data_lines = data.split(';')
            new_lines = list()
            self.write('Updating textures paths ...')
            for line in data_lines:
                line = str(line)
                if 'setAttr ".ftn" -type "string"' in line:
                    if line.endswith('.tx"') or line.endswith('.tiff"'):
                        subs = re.findall(r'"(.*?)"', line)
                        current_texture_path = subs[2]
                        for txt in current_textures_path:
                            texture_name = os.path.basename(current_texture_path)
                            if texture_name in os.path.basename(txt):
                                if not os.path.normpath(txt) == os.path.normpath(current_texture_path):
                                    line = line.replace(current_texture_path, txt).replace('/', '\\\\')
                                    self.write('>>>\n\t{0}'.format(os.path.normpath(current_texture_path)))
                                    self.write_ok('\t{0}\n'.format(os.path.normpath(txt)))
                new_lines.append(line+';')

            # Create shading file with paths fixed
            self.write('Writing new textures paths info into shading file: {}'.format(shading_path))
            with open(shading_path, 'w') as f:
                f.writelines(new_lines)
            self.write_ok('Textures Path updated successfully!')

            # Check that new shading file has a similar/close size in comparison with the original one
            orig_size = python.get_size(backup_file)
            new_size = python.get_size(shading_path)
            self.write('\nComparing backup and new shading file ...'.format(shading_path))
            diff_size = new_size - orig_size
            self.write('{0} | {1} ==> {2}\n'.format(orig_size, new_size, diff_size))
            if diff_size > 1000000:
                self.write_error('New shading file is very different from the original: {}. Textures relink process was not successful!'.format(diff_size))
                try:
                    os.remove(shading_path)
                    os.rename(backup_file, shading_path)
                except Exception as e:
                    self.write_error('Errow while recovering original shading file. Please sync shading file again!!')
                return False
            self.write_ok('Textures of Shading File have been updated successfully!\n')

            # Open shading file scene
            self.write('Opening shading file in Maya ...')
            artella.open_file_in_maya(file_path=shading_path)

            # Clean unknown nodes and old plugins for the current scene
            self.write('Cleaning unknown nodes from the asset scene ...')
            unknown_nodes = cmds.ls(type='unknown')
            if unknown_nodes and type(unknown_nodes) == list:
                for i in unknown_nodes:
                    if cmds.objExists(i):
                        if not cmds.referenceQuery(i, isNodeReferenced=True):
                            self.write_ok('Removing {} item ...'.format(i))
                            cmds.delete(i)
            unknown_nodes = cmds.ls(type='unknown')
            if unknown_nodes and type(unknown_nodes) == list:
                if len(unknown_nodes) > 0:
                    self.write_error('Error while removing unknown nodes. Please contact TD!')
                else:
                    self.write_ok('Unknown nodes removed successfully!')

            self.write('Cleaning old plugins nodes from the asset scene ...')
            old_plugins = cmds.unknownPlugin(query=True, list=True)
            if old_plugins and type(old_plugins) == list:
                for plugin in old_plugins:
                    self.write_ok('Removing {} old plugin ...'.format(plugin))
                    cmds.unknownPlugin(plugin, remove=True)
            old_plugins = cmds.unknownPlugin(query=True, list=True)
            if old_plugins and type(old_plugins) == list:
                if len(old_plugins) > 0:
                    self.write_error('Error while removing old plugins nodes. Please contact TD!')
                else:
                    self.write_ok('Old Plugins nodes removed successfully!')

            # Check that shading file has a main group with valid name
            self.write('Checking if asset main group has a valid nomenclature: {}'.format(self._asset().name))
            valid_obj = None
            if cmds.objExists(self._asset().name):
                objs = cmds.ls(self._asset().name)
                for obj in objs:
                    parent = cmds.listRelatives(obj, parent=True)
                    if parent is None:
                        valid_obj = obj
                if not valid_obj:
                    self.write_error('Main group is not valid. Please change it manually to {}\n'.format(self._asset().name))
                    return False
            else:
                self.write_error('Main group is not valid. Please change it manually to {}\n'.format(self._asset().name))
                return False
            self.write_ok('Asset main group is valid: {}\n'.format(self._asset().name))

        except Exception as e:
            self.write_error('Error while publishing shading files. Reverting process ...')
            sp.logger.error(str(e))
            self.write('Unlocking shading file ...')
            artella.unlock_file(shading_path)
            return False

        self.write('Saving change to shading file ...')
        if cmds.file(query=True, modified=True):
            cmds.file(save=True, f=True)

        self.write('Check if we need to clean Student License again ...')
        if solstice_maya_utils.file_has_student_line(filename=shading_path):
            solstice_maya_utils.clean_student_line(filename=shading_path)
            if solstice_maya_utils.file_has_student_line(filename=shading_path):
                self.write_error('After updating model path the Student License could not be fixed again!')
                return False

        # After publishing it we unlock the shading file
        self.write('Unlocking shading file ...')
        artella.unlock_file(shading_path)

        self.write_ok('------------------------------------')
        self.write_ok('SHADING PUBLISHED SUCCESSFULLY!')
        self.write_ok('------------------------------------\n\n')
        self.write('\n')

        return True


class PublishGroomTask(solstice_task.Task, object):
    def __init__(self, asset, comment='Published groom with Solstice Publisher', auto_run=False, parent=None):
        super(PublishGroomTask, self).__init__(name='PublishGroom', auto_run=auto_run, parent=parent)

        self._asset = asset
        self._comment = comment
        self.set_task_text('Publishing Groom ...')

    def run(self):
        return False


class PublishTaskGroup(solstice_taskgroups.TaskGroup, object):
    def __init__(self, asset, categories_to_publish, log=None, auto_run=False, parent=None):
        super(PublishTaskGroup, self).__init__(name='PublishAsset', log=log, parent=parent)

        # # NOTE: First we need to update textures and if textures are updated we need to update also the shading
        # # file. This is force in UI file (shading checkbox is automatically enabled if textures checkbox is enabled)
        if categories_to_publish['textures']['check']:
            categories_to_publish['shading']['check'] = True

        for cat, cat_dict in categories_to_publish.items():
            if cat_dict['check']:
                if cat == 'textures':
                    self.add_task(PublishTexturesTask(
                        asset=asset,
                        comment=cat_dict['comment'],
                        new_version=cat_dict['new_version'],
                        auto_run=auto_run
                    ))
                elif cat == 'model':
                    self.add_task(PublishModelTask(
                        asset=asset,
                        comment=cat_dict['comment'],
                        new_version=cat_dict['new_version'],
                        auto_run=auto_run
                    ))
                elif cat == 'shading':
                    self.add_task(PublishShadingTask(
                        asset=asset,
                        comment=cat_dict['comment'],
                        new_version=cat_dict['new_version'],
                        auto_run=auto_run
                    ))
                elif cat == 'groom':
                    # selected_version[cat + '/' + asset().name + '.ma'] = cat_dict['new_version_int']
                    self.add_task(PublishGroomTask(
                        asset=asset,
                        comment=cat_dict['comment'],
                        auto_run=auto_run
                    ))

        if auto_run:
            self._on_do_task()


class SolsticePublisher(solstice_dialog.Dialog, object):

    name = 'Solstice_Publisher'
    title = 'Solstice Tools - Publisher'
    version = '1.0'
    docked = False

    def __init__(self, name='SolsticePublisherWindow', asset=None, new_working_version=False, parent=None, **kwargs):
        self._asset = asset
        self._new_working_version = new_working_version
        self.result = False

        super(SolsticePublisher, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticePublisher, self).custom_ui()
        self.set_logo('solstice_publisher_logo')
        if self._asset:
            asset_publisher = AssetPublisherWidget(asset=self._asset, new_working_version=self._new_working_version)
            asset_publisher.onPublishError.connect(self.close)
            self.main_layout.addWidget(asset_publisher)
            asset_publisher.onPublishFinised.connect(self._on_publish_finished)

    def _on_publish_finished(self, bool):
        self.result = bool
        self.close()


class AssetPublisherVersionWidget(QWidget, object):

    onPublish = Signal(dict)

    def __init__(self, asset, new_working_version=False, parent=None):
        super(AssetPublisherVersionWidget, self).__init__(parent=parent)

        self._asset = asset
        self._new_working_version = new_working_version

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self._asset_icon = QLabel()
        self._asset_icon.setPixmap(
            solstice_resource.pixmap('empty_file', category='icons').scaled(200, 200, Qt.KeepAspectRatio))
        self._asset_icon.setAlignment(Qt.AlignCenter)
        if self._asset().icon:
            self._asset_icon.setPixmap(
                QPixmap.fromImage(img.base64_to_image(self._asset()._icon, image_format=self._asset()._icon_format)).scaled(300, 300, Qt.KeepAspectRatio))
        self._asset_label = QLabel(self._asset().name)
        self._asset_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self._asset_icon)
        main_layout.addWidget(self._asset_label)
        main_layout.addLayout(solstice_splitters.SplitterLayout())

        if not self._new_working_version:
            self._versions = self._asset().get_max_published_versions(all_versions=True)
        else:
            self._versions = self._asset().get_max_working_versions(all_versions=True)

        versions_layout = QGridLayout()
        versions_layout.setContentsMargins(10, 10, 10, 10)
        versions_layout.setSpacing(5)
        main_layout.addLayout(versions_layout)

        self._ui = dict()

        for i, category in enumerate(sp.valid_categories):
            self._ui[category] = dict()
            self._ui[category]['label'] = QLabel(category.upper())
            self._ui[category]['current_version'] = QLabel('v0')
            self._ui[category]['current_version'].setAlignment(Qt.AlignCenter)
            self._ui[category]['separator'] = QLabel()
            self._ui[category]['separator'].setPixmap(
                solstice_resource.pixmap('arrow_material', category='icons').scaled(QSize(24, 24)))
            self._ui[category]['next_version'] = QLabel('v0')
            self._ui[category]['next_version'].setAlignment(Qt.AlignCenter)
            self._ui[category]['check'] = QCheckBox('')
            self._ui[category]['check'].setChecked(True)
            # self._ui[category]['check'].toggled.connect(self._update_versions)
            self._ui[category]['check'].toggled.connect(self._update_ui)
            for j, widget in enumerate(['label', 'current_version', 'separator', 'next_version', 'check']):
                versions_layout.addWidget(self._ui[category][widget], i, j)

        for widget in ['label', 'current_version', 'separator', 'next_version', 'check']:
            self._ui['model'][widget].setVisible(self._asset().has_model())
            self._ui['shading'][widget].setVisible(self._asset().has_shading())
            self._ui['textures'][widget].setVisible(self._asset().has_textures())
            self._ui['groom'][widget].setVisible(self._asset().has_groom())

        main_layout.addWidget(solstice_splitters.Splitter('Comment'))
        self._comment_box = QTextEdit()
        self._comment_box.textChanged.connect(self._update_ui)
        main_layout.addWidget(self._comment_box)

        main_layout.addLayout(solstice_splitters.SplitterLayout())

        if not self._new_working_version:
            self._publish_btn = QPushButton('Publish')
        else:
            self._publish_btn = QPushButton('New Version')

        if not self._new_working_version:
            self._publish_btn.clicked.connect(self._publish)
        else:
            self._publish_btn.clicked.connect(self._new_version)

        main_layout.addWidget(self._publish_btn)

        self._update_ui()

        # Update version of the available asset files
        self._update_versions()

    def _update_versions(self):
        """
        Gets the last versions of published asset files and updates the UI properly
        """

        for cat, version in self._versions.items():
            if version is None:
                curr_version_text = 'None'
                if self._ui[cat]['check'].isChecked():
                    next_version_text = 'v1'
                else:
                    next_version_text = 'None'
            else:
                curr_version_text = 'v{0}'.format(version[0])
                if self._ui[cat]['check'].isChecked():
                    next_version_text = 'v{0}'.format(int(version[0])+1)
                else:
                    next_version_text = 'v{0}'.format(version[0])
            self._ui[cat]['current_version'].setText(curr_version_text)
            self._ui[cat]['next_version'].setText(next_version_text)

        self._update_ui()

    def _update_ui(self):
        publish_state = True

        if not self._asset().has_groom():
            if not self._ui['model']['check'].isChecked() and not self._ui['shading']['check'].isChecked() and not self._ui['textures']['check'].isChecked():
                publish_state = False
        else:
            if not self._ui['model']['check'].isChecked() and not self._ui['shading']['check'].isChecked() and not self._ui['textures']['check'].isChecked() and not self._ui['groom']['check']:
                publish_state = False

        if self._comment_box.toPlainText() is None or self._comment_box.toPlainText() == '':
            publish_state = False

        self._publish_btn.setEnabled(publish_state)

        # TODO: Textures for working assets is not ready (we should show a option to publish new version of individual
        # TODO: textures. So for now, we disable it
        if self._new_working_version:
            self._ui['textures']['check'].setChecked(False)
            self._ui['textures']['check'].setVisible(False)
            self._ui['textures']['check'].setEnabled(False)

        self._ui['shading']['check'].setEnabled(True)
        if self._ui['textures']['check'].isChecked():
            self._ui['shading']['check'].setChecked(True)
            self._ui['shading']['check'].setEnabled(False)

    def _new_version(self):
        try:
            for cat in sp.valid_categories:
                if not self._ui[cat]['check'].isChecked():
                    continue
                if not self._asset().has_category(category=cat):
                    continue

                asset_path = self._asset().asset_path
                asset_path = os.path.join(asset_path, '__working__', cat)

                comment = self._comment_box.toPlainText()

                if cat == 'textures':
                    pass
                elif cat == 'shading':
                    asset_path = os.path.join(asset_path, self._asset().name + '_SHD.ma')
                else:
                    asset_path = os.path.join(asset_path, self._asset().name + '.ma')

                artella.lock_file(file_path=asset_path)
                artella.upload_new_asset_version(file_path=asset_path, comment=comment)
                artella.unlock_file(file_path=asset_path)
        except Exception:
            from solstice_pipeline.solstice_tools import solstice_bugtracker as bug
            bug.run(traceback.format_exc())

    def _publish(self):
        try:
            categories_to_publish = dict()
            for cat in sp.valid_categories:
                categories_to_publish[cat] = dict()
                categories_to_publish[cat]['check'] = True
                if not self._ui[cat]['check'].isChecked():
                    categories_to_publish[cat]['check'] = False
                if not self._asset().has_category(category=cat):
                    categories_to_publish[cat]['check'] = False

                new_version = int(self._ui[cat]['next_version'].text()[1:])
                categories_to_publish[cat]['new_version'] = '{0:03}'.format(new_version)
                categories_to_publish[cat]['comment'] = self._comment_box.toPlainText()
                categories_to_publish[cat]['new_version_int'] = new_version

            self.onPublish.emit(categories_to_publish)
        except Exception:
            from solstice_pipeline.solstice_tools import solstice_bugtracker as bug
            bug.run(traceback.format_exc())

    # #     if cat == 'textures':
    # #         shaders, info = solstice_shaderlibrary.ShaderLibrary.export_asset(asset=self._asset())

    #         # artella.publish_asset(file_path=asset_path, comment=comment, selected_versions=selected_version)
    #         # if cat == 'textures':
    #         #     artella.synchronize_path(path=asset_path)


class AssetPublisherSummaryWidget(QWidget, object):

    onFinished = Signal(bool)

    def __init__(self, asset, parent=None):
        super(AssetPublisherSummaryWidget, self).__init__(parent=parent)

        self._error_pixmap = solstice_resource.pixmap('error', category='icons')
        self._ok_pixmap = solstice_resource.pixmap('ok', category='icons')

        self._asset = asset
        self._valid = True

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self.task_group_layout = QVBoxLayout()
        self.task_group_layout.setContentsMargins(0, 0, 0, 0)
        self.task_group_layout.setSpacing(0)

        main_layout.addLayout(self.task_group_layout)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        self._log = solstice_console.SolsticeConsole()
        self._log.write_ok('>>> SOLSTICE PUBLISHER LOG <<<\n')
        self._log.write('\n')
        main_layout.addWidget(self._log)
        main_layout.addLayout(solstice_splitters.SplitterLayout())
        self._spinner = solstice_spinner.WaitSpinner()
        main_layout.addWidget(self._spinner)

        self.ok_widget = QWidget()
        ok_splitter = solstice_splitters.SplitterLayout()
        self.ok_widget.setLayout(ok_splitter)
        self.ok_btn = QPushButton('Continue')
        self.ok_btn.clicked.connect(self._on_do_ok)
        main_layout.addWidget(self.ok_widget)
        main_layout.addWidget(self.ok_btn)
        self.ok_widget.setVisible(False)
        self.ok_btn.setVisible(False)

    def set_task_group(self, task_group):
        self.task_group_layout.addWidget(task_group)
        task_group.set_log(self._log)
        task_group.taskFinished.connect(self._on_task_finished)
        task_group._on_do_task()

    def _on_do_ok(self):
        self.onFinished.emit(self._valid)

    def _on_task_finished(self, valid):
        if valid is False:
            self._valid = valid

        self._spinner._timer.timeout.disconnect()
        if self._valid:
            self._spinner.thumbnail_label.setPixmap(self._ok_pixmap)
        else:
            self._spinner.thumbnail_label.setPixmap(self._error_pixmap)

        self.ok_widget.setVisible(True)
        self.ok_btn.setVisible(True)


class AssetPublisherWidget(QWidget, object):

    onPublishError = Signal()
    onPublishFinised = Signal(bool)

    def __init__(self, asset, new_working_version=False, parent=None):
        super(AssetPublisherWidget, self).__init__(parent=parent)

        self._asset = weakref.ref(asset)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self.stack_widget = QStackedWidget()
        main_layout.addWidget(self.stack_widget)

        self.version_widget = AssetPublisherVersionWidget(asset=self._asset, new_working_version=new_working_version)
        self.summary_widget = AssetPublisherSummaryWidget(asset=self._asset)
        self.version_widget.onPublish.connect(self._publish)

        self.stack_widget.addWidget(self.version_widget)
        self.stack_widget.addWidget(self.summary_widget)

        self.summary_widget.onFinished.connect(self._on_summary_finish)

        # =====================================================================================================

        # TODO: Uncomment after testing
        # for cat in sp.valid_categories:
        #     asset_locked_by, current_user_can_lock = self._asset().is_locked(category=cat, status='working')
        #     if asset_locked_by:
        #         if not current_user_can_lock:
        #             self._ui[cat]['check'].setChecked(False)
        #             self._ui[cat]['current_version'].setText('LOCK')
        #             self._ui[cat]['next_version'].setText('LOCK')
        #             for name, w in self._ui[cat].items():
        #                 w.setEnabled(False)

    def _publish(self, categories_to_publish):
        try:
            self.stack_widget.setCurrentIndex(1)
            self.summary_widget.set_task_group(PublishTaskGroup(
                asset=self._asset,
                categories_to_publish=categories_to_publish,
                log=self.summary_widget._log
            ))
        except Exception:
            from solstice_pipeline.solstice_tools import solstice_bugtracker as bug
            self.onPublishError.emit()
            bug.run(traceback.format_exc())

    def _on_summary_finish(self, valid):
        self.onPublishFinised.emit(valid)


def run(asset=None, new_working_version=False):
    reload(solstice_validators)
    from solstice_pipeline.solstice_checks import solstice_assetchecks
    reload(solstice_assetchecks)
    reload(solstice_spinner)

    publisher_dialog = SolsticePublisher(asset=asset, new_working_version=new_working_version)
    publisher_dialog.exec_()
    return publisher_dialog.result