#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_anim_utils.py
# by Tomas Poveda
# Collection of utils functions for animation
# ______________________________________________________________________
# ==================================================================="""

import maya.cmds as cmds

from pipeline.utils import mayautils as utils


def space_switch_match(node, attr_name, attr_value):
    key_when_switching = False
    if cmds.keyframe(node, query=True):
        key_when_switching = True
    if key_when_switching:
        current_time_frame = cmds.currentTime(query=True)
        frame_before = current_time_frame  -1
        cmds.setKeyframe(node, breakdown=0, hierarchy='none', controlPoints=0, shape=False, t=frame_before)
    temp_loc = cmds.spaceLocator(n='temp_{}_loc'.format(node))
    temp_a = cmds.pointConstraint(node, temp_loc[0])
    temp_b = cmds.orientConstraint(node, temp_loc[0])
    cmds.delete(temp_a, temp_b)
    cmds.setAttr('{}.{}'.format(node, attr_name), attr_value)
    temp_cons = list()
    lock_pos_attrs = utils.get_locked_attributes(node, 'translate')
    lock_rot_attrs = utils.get_locked_attributes(node, 'rotate')
    if lock_pos_attrs != 'none':
        if len(lock_pos_attrs) < 3:
            temp_a = cmds.pointConstraint(temp_loc, node, skip=lock_pos_attrs)[0]
            temp_cons.append(temp_a)
    else:
        temp_a = cmds.pointConstraint(temp_loc, node)[0]
        temp_cons.append(temp_a)
    if lock_rot_attrs != 'none':
        if len(lock_rot_attrs) < 3:
            temp_b = cmds.orientConstraint(temp_loc, node, skip=lock_rot_attrs)[0]
            temp_cons.append(temp_b)
    else:
        temp_b = cmds.orientConstraint(temp_loc, node)[0]
        temp_cons.append(temp_b)

    if key_when_switching:
        cmds.setKeyframe(node, breakdown=0, hierarchy='none', controlPoints=0, shape=1)
        if temp_cons:
            cmds.delete(temp_cons)
    cmds.delete(temp_loc)


def bake_space_switch(node, attr_name, attr_value, frame_range=None):
    if frame_range is None:
        frame_range = list()
    if len(frame_range) < 2:
        return

    start_frame = int(frame_range[0])
    end_frame = int(frame_range[-1])
    cmds.setKeyframe(node, breakdown=0, hierarchy='none', controlPoints=0, shape=False, t=start_frame-1)
    lock_pos_attrs = utils.get_locked_attributes(node, 'translate')
    lock_rot_attrs = utils.get_locked_attributes(node, 'rotate')
    point_cns_valid = True
    orient_cns_valid = True
    if lock_pos_attrs != 'none':
        if not len(lock_pos_attrs) < 3:
            point_cns_valid = False
    if lock_rot_attrs != 'none':
        if not len(lock_rot_attrs) < 3:
            orient_cns_valid = False
    cmds.setKeyframe(node, at=[
        attr_name,
        'rotateX',
        'rotateY',
        'rotateZ',
        'translateX',
        'translateY',
        'translateZ'], t=list(range(start_frame, end_frame + 1)), i=True, respectKeyable=True)
    for frame in range(start_frame, end_frame+1):
        cmds.currentTime(frame, e=True, update=True)
        temp_loc = cmds.spaceLocator(n='temp_{}_loc'.format(node))
        temp_a = cmds.pointConstraint(node, temp_loc[0])
        temp_b = cmds.orientConstraint(node, temp_loc[0])
        cmds.delete(temp_a, temp_b)
        cmds.setAttr('{}.{}'.format(node, attr_name), attr_value)
        temp_cons = list()
        if point_cns_valid:
            temp_a = cmds.pointConstraint(temp_loc, node, skip=lock_pos_attrs)[0]
            temp_cons.append(temp_a)
        if orient_cns_valid:
            temp_b = cmds.orientConstraint(temp_loc, node, skip=lock_rot_attrs)[0]
            temp_cons.append(temp_b)
        cmds.setKeyframe(node, breakdown=0, hierarchy='none', controlPoints=0, shape=0)
        if temp_cons:
            cmds.delete(temp_cons)
        cmds.delete(temp_loc)

def get_timeline_range():
    time_range = list()
    time_range.append(cmds.playbackOptions(animationStartTime=True, query=True))
    time_range.append(cmds.playbackOptions(animationEndTime=True, query=True))

    return time_range

def get_playback_range():
    time_range = list()
    time_range.append(cmds.playbackOptions(minTime=True, query=True))
    time_range.append(cmds.playbackOptions(maxTime=True, query=True))

    return time_range
