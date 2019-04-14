#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utility functions related with rigging
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import maya.cmds as cmds

import solstice.pipeline as sp
from solstice.pipeline.utils import mayautils


def create_circle_control(name, color_index=1, radius=5, move_y=0):
    """
    Creates basic circle control for rigs
    :param name: str, name of the control
    :param color_index: int, index that defines the color for the control (from 0 to 31)
    :param radius: float, radius of the circle
    :param move_y: float, offset in Y world axis for the control
    :return: str, name of the new control
    """

    ctrl_info = dict()
    new_name = name.replace('_', '')
    ctrl_info['offset'] = cmds.group(name='{}_offset'.format(new_name), empty=True, world=True)
    ctrl_info['constraint'] = cmds.group(name='{}_constraint'.format(name), empty=True, parent=ctrl_info['offset'])
    ctrl_info['main'] = cmds.group(name='{}_grp'.format(new_name), empty=True, parent=ctrl_info['constraint'])
    ctrl_info['control'] = cmds.circle(name=name, normal=[0, 1, 0], radius=radius)[0]
    cmds.move(0, move_y, 0, ctrl_info['control'])
    cmds.parent(ctrl_info['control'], ctrl_info['main'])
    ctrl_shape = cmds.listRelatives(ctrl_info['control'], shapes=True)[0]
    cmds.setAttr(ctrl_shape + '.overrideEnabled', True)
    cmds.setAttr(ctrl_shape + '.overrideColor', color_index)

    return ctrl_info


def lock_xforms(name, lock_visibility=False):
    """
    Util function to lock rig controls transforms easily
    :param name: str, name of the control we want to lock transform channels of
    :param lock_visibility: bool, Whether visibility needs to be also locked or not
    """

    for axis in ['x', 'y', 'z']:
        for xform in ['t', 'r', 's']:
            cmds.setAttr('{}.{}{}'.format(name, xform, axis), lock=True, keyable=False, channelBox=False)
    if lock_visibility:
        cmds.setAttr('{}.visibility'.format(name), lock=True, keyable=False, channelBox=False)


@mayautils.maya_undo
def create_basic_asset_rig(main_grp=None, reduction=60):
    """
    Function that creates a basic rig for the given asset group name
    If no group name is given the selected group will be used
    :param main_grp: str
    :param reduction: int, level of reduction for proxy mesh
    """

    if main_grp is None:
        main_grp = cmds.ls(sl=True)
        if not main_grp:
            cmds.confirmDialog(
                title='Impossible to create basic rig',
                message='Before executing script select main asset group with proper Solstice Nomenclature',
                icon='warning'
            )
            return
        main_grp = main_grp[0]

    if not cmds.objExists(main_grp):
        return

    sp.logger.debug('Creating Asset Rig for: {}'.format(main_grp))

    rig_grp = cmds.group(name='rig', empty=True, world=True)
    proxy_grp = cmds.group(name='proxy', empty=True, world=True)
    hires_grp = cmds.group(name='hires', empty=True, world=True)

    ctrl_grp = cmds.group(name='control_grp', empty=True, parent=rig_grp)
    extra_grp = cmds.group(name='extra_grp', empty=True, parent=rig_grp)

    joint_proxy_grp = cmds.group(name='joint_proxy', empty=True, parent=proxy_grp)
    mesh_proxy_grp = cmds.group(name='mesh_proxy', empty=True, parent=proxy_grp)
    proyx_asset_grp = cmds.group(name='{}_proxy_grp'.format(main_grp), empty=True, parent=mesh_proxy_grp)

    joint_hires_grp = cmds.group(name='joint_hires', empty=True, parent=hires_grp)
    mesh_hires_grp = cmds.group(name='mesh_hires', empty=True, parent=hires_grp)
    hires_asset_grp = cmds.group(name='{}_hires_grp'.format(main_grp), empty=True, parent=mesh_hires_grp)

    root_info = create_circle_control('root_ctrl', radius=15, color_index=29)
    main_info = create_circle_control('main_ctrl', radius=13, color_index=16, move_y=1)
    cmds.parent(main_info['offset'], root_info['control'])
    cmds.parent(root_info['offset'], ctrl_grp)

    # =============================================================================

    cmds.parentConstraint(main_info['control'], proyx_asset_grp, mo=False)
    cmds.scaleConstraint(main_info['control'], proyx_asset_grp, mo=False)
    cmds.parentConstraint(main_info['control'], hires_asset_grp, mo=False)
    cmds.scaleConstraint(main_info['control'], hires_asset_grp, mo=False)

    # =============================================================================

    lock_xforms(rig_grp)
    lock_xforms(proxy_grp)
    lock_xforms(hires_grp)
    lock_xforms(ctrl_grp)
    lock_xforms(extra_grp)
    lock_xforms(joint_proxy_grp)
    lock_xforms(mesh_proxy_grp)
    lock_xforms(joint_hires_grp)
    lock_xforms(mesh_hires_grp)
    lock_xforms(main_grp)

    # =============================================================================
    try:
        cmds.addAttr(main_grp, ln='type', at='enum', en='proxy:hires:both')
    except:
        pass
    cmds.setAttr('{}.type'.format(main_grp), edit=True, keyable=False)
    cmds.setAttr('{}.type'.format(main_grp), edit=True, channelBox=False)

    cmds.setAttr('{}.type'.format(main_grp), 0)
    cmds.setAttr('{}.visibility'.format(proxy_grp), True)
    cmds.setAttr('{}.visibility'.format(hires_grp), False)
    cmds.setDrivenKeyframe(proxy_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setDrivenKeyframe(hires_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setAttr('{}.type'.format(main_grp), 1)
    cmds.setAttr('{}.visibility'.format(proxy_grp), False)
    cmds.setAttr('{}.visibility'.format(hires_grp), True)
    cmds.setDrivenKeyframe(proxy_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setDrivenKeyframe(hires_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setAttr('{}.type'.format(main_grp), 2)
    cmds.setAttr('{}.visibility'.format(proxy_grp), True)
    cmds.setAttr('{}.visibility'.format(hires_grp), True)
    cmds.setDrivenKeyframe(proxy_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setDrivenKeyframe(hires_grp + '.visibility', currentDriver='{}.type'.format(main_grp))
    cmds.setAttr('{}.type'.format(main_grp), 0)

    # =============================================================================

    dup_meshes = list()
    childs = cmds.listRelatives(main_grp, children=True, fullPath=True)
    for child in childs:
        dup_meshes.append(cmds.duplicate(child)[0])
        cmds.parent(child, hires_asset_grp)

    cmds.parent(rig_grp, main_grp)
    cmds.parent(proxy_grp, main_grp)
    cmds.parent(hires_grp, main_grp)

    if len(dup_meshes) > 1:
        combine_mesh = cmds.polyUnite(dup_meshes, name='{}_proxy'.format(main_grp), ch=False)
    else:
        combine_mesh = dup_meshes[0]
        cmds.rename(combine_mesh, '{}_proxy'.format(main_grp))
        combine_mesh = '{}_proxy'.format(main_grp)

    try:
        cmds.polyReduce(combine_mesh, ver=1, trm=0, shp=0, keepBorder=1, keepMapBorder=1, keepColorBorder=1,
                        keepFaceGroupBorder=1, keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight=0.5,
                        keepMapBorderWeight=0.5, keepColorBorderWeight=0.5, keepFaceGroupBorderWeight=0.5,
                        keepHardEdgeWeight=0.5, keepCreaseEdgeWeight=0.5, useVirtualSymmetry=0, symmetryTolerance=0.01,
                        sx=0, sy=1, sz=0, sw=0, preserveTopology=1, keepQuadsWeight=1, vertexMapName="", cachingReduce=1,
                        ch=1, p=reduction, vct=0, tct=0, replaceOriginal=1)
    except Exception as e:
        sp.logger.warning('Impossible to reduce proxy mesh: {}'.format(e))

    # cmds.polyReduce(combine_mesh, percentage=95, ch=False)
    cmds.parent(combine_mesh, proyx_asset_grp)

    sp.message('Basic asset rig created for {} successfully!'.format(main_grp))

# =============================================================================

@mayautils.maya_undo
def update_model_meshes(orig_group=None, new_group=None):
    if orig_group is None or new_group is None or not cmds.objExists(orig_group) or not cmds.objExists(new_group):
        sel = cmds.ls(sl=True)
        if len(sel) <= 0 or len(sel) > 2:
            cmds.warning('Select original group and new group')
            return
        orig_group = sel[0]
        new_group = sel[1]

    orig_meshes = [obj for obj in cmds.listRelatives(orig_group, type='transform', fullPath=True) if
                   cmds.listRelatives(obj, shapes=True)]
    new_meshes = [obj for obj in cmds.listRelatives(new_group, type='transform', fullPath=True) if
                  cmds.listRelatives(obj, shapes=True)]

    if len(orig_meshes) != len(new_meshes):
        cmds.warning('Meshes are not the same in the selected groups')
        return

    # Position new meshes properly
    processed_meshes = list()
    for orig_mesh in orig_meshes:
        orig_name = orig_mesh.split('|')[-1]
        for new_mesh in new_meshes:
            new_name = new_mesh.split('|')[-1]
            if orig_name == new_name:
                cmds.delete(cmds.parentConstraint(orig_mesh, new_mesh, mo=False)[0])
                processed_meshes.append(orig_name)

    if len(processed_meshes) != len(new_meshes):
        cmds.warning('Some meshes are not on both groups')
        return

    # Delete original meshes
    cmds.delete(orig_meshes)

    # Parent new meshes into original meshes group, assing basic lambert shader and lock transform attributes
    for mesh in new_meshes:
        cmds.makeIdentity(mesh, apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.sets(mesh, edit=True, forceElement='initialShadingGroup')
        for axis in ['x', 'y', 'z']:
            for xform in ['t', 'r', 's']:
                cmds.setAttr('{0}.{1}{2}'.format(mesh, xform, axis), lock=True)
        cmds.setAttr(mesh + '.v', lock=True)
        cmds.parent(mesh, orig_group)

    # Delete new group
    cmds.delete(new_group)

# =============================================================================


def check_shaders_nomenclature(name=None):
    """
    Function that checks that shaders nomenclature is valid
    :param name: str, name of the object to select. If None, first selected object will be checked
    """

    if name is None or not cmds.objExists(name):
        sel = cmds.ls(sl=True)
        if not sel:
            sp.logger.warning('No shaders to check. Please select an object!')
            return
        name = sel[0]

    shader_types = cmds.listNodeTypes('shader')
    shaders = cmds.ls(materials=True)
    for shader in shaders:
        if shader in ['lambert1', 'particleCloud1']:
            continue
        if 'displacement' in shader or 'Displacement' in shader:
            continue
        if not shader.startswith(name):
            cmds.warning('{} should start with {}'.format(shader, name))
        shading_groups = cmds.listConnections(shader, type='shadingEngine')
        if shading_groups:
            shading_grp = shading_groups[0]
            connections = cmds.listConnections(shading_grp, source=True, destination=False)
            if connections is not None:
                connected_shaders = list()
                for cnt in connections:
                    if cmds.objectType(cnt) in shader_types:
                        connected_shaders.append(cnt)
                    if len(connected_shaders) > 0:
                        target_name = cmds.listConnections(shading_grp + '.surfaceShader')[0]
                    if shading_grp != '{}SG'.format(target_name, shader):
                        cmds.warning('{} ---------- {} => {}'.format(target_name, shader, shading_grp))
            else:
                if shading_grp != '{}_{}SG'.format(name, shader):
                    cmds.warning('{} => {}'.format(shader, shading_grp))


@mayautils.maya_undo
def rename_shaders(name=None):
    """
    Rename all the shaders of the given object. If None, first selected element shaders will be renamed
    :param name: str
    """

    if name is None or not cmds.objExists(name):
        sel = cmds.ls(sl=True)
        if not sel:
            sp.logger.warning('No shaders to rename. Please select an object!')
            return
        name = sel[0]

    shader_types = cmds.listNodeTypes('shader')
    shaders = cmds.ls(materials=True)
    for shader in shaders:
        try:
            if shader in ['lambert1', 'particleCloud1']:
                continue
            shading_groups = cmds.listConnections(shader, type='shadingEngine')
            if shading_groups:
                for shading_grp in shading_groups:
                    connections = cmds.listConnections(shading_grp, source=True, destination=False)
                    if connections is not None:
                        connected_shaders = list()
                        for cnt in connections:
                            if cmds.objectType(cnt) in shader_types:
                                connected_shaders.append(cnt)
                            if len(connected_shaders) > 0:
                                target_name = cmds.listConnections(shading_grp + '.surfaceShader')[0]
                                if shading_grp != '{}SG'.format(target_name, shader):
                                    cmds.rename(shading_grp, '{}SG'.format(target_name, shader))
                    else:
                        if shading_grp != '{}_{}SG'.format(name, shader):
                            cmds.rename(shading_grp, '{}_{}SG'.format(name, shader))
            if not shader.startswith(name):
                cmds.rename(shader, '{}_{}'.format(name, shader))
        except Exception as e:
            cmds.warning('Skipping shader {}'.format(shader))
            sp.logger.error(str(e))
