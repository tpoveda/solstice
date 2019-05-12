#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class to create prop rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import json
import  math

import solstice.pipeline as sp
from solstice.pipeline.core import asset as core_asset
from solstice.pipeline.tools.autorigger.core import control, utils
from solstice.pipeline.tools.tagger import tagger

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.utils import mayautils
    from solstice.pipeline.tools.shaderlibrary import shaderlibrary

reload(core_asset)
reload(control)
reload(utils)


class AssetRig(object):
    """
    Base class to create asset rigs
    """

    def __init__(self, asset):
        super(AssetRig, self).__init__()

        self._main_grp = None
        self._rig_grp = None
        self._proxy_grp = None
        self._hires_grp = None
        self._ctrl_grp = None
        self._extra_grp = None
        self._joint_proxy_grp = None
        self._mesh_proxy_grp = None
        self._proxy_asset_grp = None
        self._joint_hires_grp = None
        self._mesh_hires_grp = None
        self._hires_asset_grp = None

        self._root_ctrl = None
        self._main_ctrl = None

        self._geo = dict()
        self._builder_grp = None
        self._builder_locators = list()
        self._main_constraints = list()

        if isinstance(asset, core_asset.AssetWidget):
           self._asset = asset
        elif isinstance(asset, (str, unicode, basestring)):
            self._asset = sp.find_asset(asset)
        else:
            raise Exception('Given Asset is not valid!'.format(asset))

    def build(self, force_new=True):
        """
        Main function to build the rig
        """

        sp.dcc.new_file(force=force_new)

        print('Building rig for asset {}'.format(self._asset.name))

        self.create_main_groups()
        self.import_model()
        self.import_proxy()
        self.import_builder()

        self.create_main_controls()
        self.create_main_attributes()
        self.connect_main_controls()

        self.clean_model_group()
        self.clean_proxy_group()

        self.setup()

        self.finish()

        cmds.select(cmds.ls())
        cmds.viewFit(animate=True)
        cmds.select(clear=True)

    def create_main_groups(self):
        """
        Function that creates main rig groups
        """

        self._main_grp = cmds.group(name=self._asset.name, empty=True, world=True)
        self._rig_grp = cmds.group(name='rig', empty=True, parent=self._main_grp)
        self._proxy_grp = cmds.group(name='proxy', empty=True, parent=self._main_grp)
        self._hires_grp = cmds.group(name='hires', empty=True, parent=self._main_grp)
        self._ctrl_grp = cmds.group(name='control_grp', empty=True, parent=self._rig_grp)
        self._extra_grp = cmds.group(name='extra_grp', empty=True, parent=self._rig_grp)
        self._joint_proxy_grp = cmds.group(name='joint_proxy', empty=True, parent=self._proxy_grp)
        self._mesh_proxy_grp = cmds.group(name='mesh_proxy', empty=True, parent=self._proxy_grp)
        self._proxy_asset_grp = cmds.group(name='{}_proxy_grp'.format(self._main_grp), empty=True, parent=self._mesh_proxy_grp)
        self._joint_hires_grp = cmds.group(name='joint_hires', empty=True, parent=self._hires_grp)
        self._mesh_hires_grp = cmds.group(name='mesh_hires', empty=True, parent=self._hires_grp)
        self._hires_asset_grp = cmds.group(name='{}_hires_grp'.format(self._main_grp), empty=True, parent=self._mesh_hires_grp)

    def create_main_controls(self):
        """
        Function that creates main rig controls
        """

        xmin, ymin, zmin, xmax, ymax, zmax = cmds.exactWorldBoundingBox(self._geo['model'])
        a = [xmin, 0, 0]
        b = [xmax, 0, 0]
        radius = (math.sqrt(pow(a[0]-b[0], 2)+pow(a[1]-b[1], 2)+pow(a[2]-b[2], 2)))

        self._root_ctrl = control.Circle('root', normal=[0, 1, 0], radius=radius, color_index=29)
        self._main_ctrl = control.Circle('main', normal=[0, 1, 0], radius=radius-6, color_index=16)
        self._main_ctrl.move(0, 2, 0)

    def create_main_attributes(self):
        """
        Function that create main rig attributes
        """

        assert self._main_grp and sp.dcc.object_exists(self._main_grp)

        cmds.addAttr(self._main_grp, ln='type', at='enum', en='proxy:hires:both')
        cmds.setAttr('{}.type'.format(self._main_grp), edit=True, keyable=False)
        cmds.setAttr('{}.type'.format(self._main_grp), edit=True, channelBox=False)
        cmds.setAttr('{}.type'.format(self._main_grp), 0)
        cmds.setAttr('{}.visibility'.format(self._proxy_grp), True)
        cmds.setAttr('{}.visibility'.format(self._hires_grp), False)
        cmds.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setAttr('{}.type'.format(self._main_grp), 1)
        cmds.setAttr('{}.visibility'.format(self._proxy_grp), False)
        cmds.setAttr('{}.visibility'.format(self._hires_grp), True)
        cmds.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setAttr('{}.type'.format(self._main_grp), 2)
        cmds.setAttr('{}.visibility'.format(self._proxy_grp), True)
        cmds.setAttr('{}.visibility'.format(self._hires_grp), True)
        cmds.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        cmds.setAttr('{}.type'.format(self._main_grp), 1)

    def connect_main_controls(self):
        """
        Function that connects main controls
        """

        assert self._main_ctrl and sp.dcc.object_exists(self._main_ctrl.node)
        assert self._root_ctrl and sp.dcc.object_exists(self._root_ctrl.node)
        assert self._proxy_asset_grp and sp.dcc.object_exists(self._proxy_asset_grp)
        assert self._hires_asset_grp and sp.dcc.object_exists(self._hires_asset_grp)

        sp.dcc.set_parent(self._main_ctrl.offset, self._root_ctrl.node)
        sp.dcc.set_parent(self._root_ctrl.offset, self._ctrl_grp)

        self._main_constraints.append(cmds.parentConstraint(self._main_ctrl.node, self._proxy_asset_grp, mo=False))
        self._main_constraints.append(cmds.scaleConstraint(self._main_ctrl.node, self._proxy_asset_grp, mo=False))
        self._main_constraints.append(cmds.parentConstraint(self._main_ctrl.node, self._hires_asset_grp, mo=False))
        self._main_constraints.append(cmds.scaleConstraint(self._main_ctrl.node, self._hires_asset_grp, mo=False))

    def import_model(self):
        """
        Function that import latest working file of the asset model
        """

        if not sp.is_maya():
            sp.logger.warning('Import model functionality is only available in Maya')
            return

        assert self._asset

        track = mayautils.TrackNodes()
        track.load('transform')
        self._asset.import_model_file(status='working')
        cmds.refresh()
        imported_objs = track.get_delta()
        self._geo['model'] = imported_objs
        cmds.select(imported_objs)
        cmds.viewFit(animate=True)
        cmds.select(clear=True)

    def import_proxy(self):
        """
        Function that imports latest working file of the asset proxy model
        """

        if not sp.is_maya():
            sp.logger.warning('Import proxy model functionality is only available in Maya')
            return

        assert self._asset

        track = mayautils.TrackNodes()
        track.load('transform')
        self._asset.import_proxy_file()
        cmds.refresh()
        imported_objs = track.get_delta()
        self._geo['proxy'] = imported_objs
        cmds.select(imported_objs)
        cmds.viewFit(animate=True)
        cmds.select(clear=True)

    def import_builder(self):
        """
        Function that imports in the scene the builder file
        """

        if not sp.is_maya():
            sp.logger.warning('Import builder functionality is only available in Maya')
            return

        assert self._asset

        track = mayautils.TrackNodes()
        track.load('transform')
        track = mayautils.TrackNodes()
        track.load('transform')
        self._asset.import_builder_file()
        cmds.refresh()
        imported_objs = track.get_delta()
        cmds.select(imported_objs)
        cmds.viewFit(animate=True)
        cmds.select(clear=True)

    def clean_model_group(self):
        """
        Function that clean model group contents
        """

        assert self._hires_asset_grp and sp.dcc.object_exists(self._hires_asset_grp)

        model_grp = '{}_MODEL'.format(self._asset.name)
        if not sp.dcc.object_exists(model_grp):
            sp.logger.warning('Model Group with name {} does not exists!'.format(model_grp))
            return

        children = sp.dcc.list_children(model_grp, full_path=True, children_type='transform')
        for child in children:
            sp.dcc.set_parent(child, self._hires_asset_grp)

        sp.dcc.delete_object(model_grp)

    def clean_proxy_group(self):
        """
        Function that clean proxy model group contents
        """

        assert self._proxy_asset_grp and sp.dcc.object_exists(self._proxy_asset_grp)

        proxy_grp = '{}_PROXY'.format(self._asset.name)
        if not sp.dcc.object_exists(proxy_grp):
            sp.logger.warning('Proxy Model Group with name {} does not exists!'.format(proxy_grp))
            return

        children = sp.dcc.list_children(proxy_grp, full_path=True, children_type='transform')
        for child in children:
            sp.dcc.set_parent(child, self._proxy_asset_grp)

        sp.dcc.delete_object(proxy_grp)

    def setup(self):
        """
        This function MUST be override in specific rigs
        Use this function to create custom rig code
        """

        builder_grp = '{}_BUILDER'.format(self._asset.name)
        if not sp.dcc.object_exists(builder_grp):
            sp.logger.warning('Builder Group with name {} does not exists!'.format(builder_grp))
            return

        self._builder_grp = builder_grp
        self._builder_locators = sp.dcc.list_children(builder_grp, full_path=False, children_type='transform')

    def finish(self):
        """
        Function that is called before ending rig setup
        """

        if self._builder_grp and sp.dcc.object_exists(self._builder_grp):
            sp.dcc.delete_object(self._builder_grp)

        utils.lock_all_transforms(self._rig_grp)
        utils.lock_all_transforms(self._proxy_grp)
        utils.lock_all_transforms(self._hires_grp)
        utils.lock_all_transforms(self._ctrl_grp)
        utils.lock_all_transforms(self._extra_grp)
        utils.lock_all_transforms(self._joint_proxy_grp, lock_visibility=True)
        utils.lock_all_transforms(self._mesh_proxy_grp)
        utils.lock_all_transforms(self._proxy_asset_grp)
        utils.lock_all_transforms(self._joint_hires_grp, lock_visibility=True)
        utils.lock_all_transforms(self._mesh_hires_grp)
        utils.lock_all_transforms(self._hires_asset_grp)
        utils.lock_all_transforms(self._main_grp)

        self._setup_tag()

    def _setup_tag(self):
        """
        Internal function used to setup tag attribute in the rig
        """

        valid_obj = None
        if sp.dcc.object_exists(self._asset.name):
            objs = sp.dcc.list_nodes(node_name=self._asset.name)
            for obj in objs:
                parent = sp.dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                sp.logger.error('Main group is not valid. Please change it manually to {}'.format(self._asset.name))
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
            sp.logger.warning('Main group has not a valid tag data node connected to it. Creating it ...')
            try:
                sp.dcc.select_object(valid_obj)
                tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(self._asset.category)
                sp.dcc.clear_selection()
                valid_tag_data = False
                main_group_connections = sp.dcc.list_source_destination_connections(valid_obj)
                for connection in main_group_connections:
                    attrs = sp.dcc.list_user_attributes(connection)
                    if attrs and type(attrs) == list:
                        for attr in attrs:
                            if attr == 'tag_type':
                                valid_tag_data = True
                if not valid_tag_data:
                    sp.logger.error('Impossible to create tag data node. Please contact TD team to fix this ...')
                    return False
            except Exception as e:
                sp.logger.error('Impossible to create tag data node. Please contact TD team to fix this ...')
                sp.logger.error(str(e))
                return False

        tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
            sp.logger.error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        # Connect proxy group to tag data node
        valid_connection = tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if not valid_connection:
            sp.logger.error(
                'Error while connecting Proxy Group to tag data node!  Check Maya editor for more info about the error!')
            return False

        # Connect hires group to tag data node
        valid_connection = tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if not valid_connection:
            sp.logger.error(
                'Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            return False

        # Getting shaders info data
        shaders_file = shaderlibrary.ShaderLibrary.get_asset_shader_file_path(asset=self._asset)
        if not os.path.exists(shaders_file):
            sp.logger.error(
                'Shaders JSON file for asset {0} does not exists: {1}'.format(self._asset.name, shaders_file))
            return False

        with open(shaders_file) as f:
            shader_data = json.load(f)
        if shader_data is None:
            sp.logger.error(
                'Shaders JSON file for asset {0} is not valid: {1}'.format(self._asset.name, shaders_file))
            return False

        hires_grp = None
        hires_grp_name = '{}_hires_grp'.format(self._asset.name)
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
                            sp.logger.error('Multiple Hires groups in the file. Please check it!')
                            return False
        if not hires_grp:
            sp.logger.error('No hires group found ...')
            return False
        hires_meshes = sp.dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True,
                                             relative_type='transform')

        # Checking if shader data is valid
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
                sp.logger.error('Mesh {} not found in both model and shading file ...'.format(mesh_name))
                valid_meshes = False
        if not valid_meshes:
            sp.logger.error('Some shading meshes and model hires meshes are missed. Please contact TD!')
            return False

        # Create if necessary shaders attribute in model tag data node
        if not tag_data_node or not sp.dcc.object_exists(tag_data_node):
            sp.logger.error('Tag data does not exists in the current scene!'.format(tag_data_node))
            return False

        attr_exists = sp.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
        if attr_exists:
            sp.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')
        else:
            sp.dcc.add_string_attribute(node=tag_data_node, attribute_name='shaders')
            attr_exists = sp.dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
            if not attr_exists:
                sp.logger.error('No Shaders attribute found on model tag data node: {}'.format(tag_data_node))
                return False

        sp.dcc.unlock_attribute(node=tag_data_node, attribute_name='shaders')
        sp.dcc.set_string_attribute_value(node=tag_data_node, attribute_name='shaders', attribute_value=shader_data)
        sp.dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')

        return True





