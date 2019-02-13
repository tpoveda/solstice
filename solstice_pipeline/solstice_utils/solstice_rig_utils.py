#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_rig_utils.py
# by Tomas Poveda
# Module that contains utility functions related with rigging
# ______________________________________________________________________
# ==================================================================="""

import maya.cmds as cmds

import solstice_pipeline as sp
from solstice_pipeline.solstice_utils import solstice_maya_utils
from solstice_pipeline.solstice_gui import solstice_traymessage
reload(solstice_traymessage)


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


@solstice_maya_utils.maya_undo
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
    cmds.polyReduce(combine_mesh, ver=1, trm=0, shp=0, keepBorder=1, keepMapBorder=1, keepColorBorder=1,
                    keepFaceGroupBorder=1, keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight=0.5,
                    keepMapBorderWeight=0.5, keepColorBorderWeight=0.5, keepFaceGroupBorderWeight=0.5,
                    keepHardEdgeWeight=0.5, keepCreaseEdgeWeight=0.5, useVirtualSymmetry=0, symmetryTolerance=0.01,
                    sx=0, sy=1, sz=0, sw=0, preserveTopology=1, keepQuadsWeight=1, vertexMapName="", cachingReduce=1,
                    ch=1, p=reduction, vct=0, tct=0, replaceOriginal=1)

    # cmds.polyReduce(combine_mesh, percentage=95, ch=False)
    cmds.parent(combine_mesh, proyx_asset_grp)

    sp.message('Basic asset rig created for {} successfully!'.format(main_grp))
