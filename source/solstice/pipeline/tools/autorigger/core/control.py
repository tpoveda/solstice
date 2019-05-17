#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for rig controls
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.tools.autorigger.core import naming

if sp.is_maya():
    import maya.cmds as cmds
    from solstice.pipeline.utils import mayautils

reload(naming)
reload(mayautils)


class RigControl(object):
    def __init__(
            self,
            node,
            parent='',
            translate_to='', rotate_to='',
            lock_channels=None,
            create_offset_group=True, create_auto_group=True, create_constraint_group=True,
            auto_rename=True,
            color_index=-1):

        if lock_channels is None:
            lock_channels = ['v']

        self._node = None
        self._root = None
        self._offset = None
        self._constraint = None
        self._auto = None

        ctrl_new_name = node
        if auto_rename:
            ctrl_new_name = naming.build_name(node, naming.Names.Control)
            sp.dcc.rename_node(node, ctrl_new_name)

        ctrl_shapes = sp.dcc.list_shapes(ctrl_new_name, full_path=True)
        for shp in ctrl_shapes:
            sp.dcc.set_integer_attribute_value(shp, 'ove', True)
            sp.dcc.set_integer_attribute_value(shp, 'ovc', True)
            if color_index > -1 and color_index < 32:
                sp.dcc.set_integer_attribute_value(shp, 'ovc', color_index)
            else:
                if ctrl_new_name.startswith('l_') or ctrl_new_name.endswith('_l') or '_l_' in ctrl_new_name:
                    sp.dcc.set_integer_attribute_value(shp, 'ovc', 6)
                elif ctrl_new_name.startswith('r_') or ctrl_new_name.endswith('_r') or '_r_' in ctrl_new_name:
                    sp.dcc.set_integer_attribute_value(shp, 'ovc', 13)
                else:
                    sp.dcc.set_integer_attribute_value(shp, 'ovc', 22)

        self._node = ctrl_new_name

        self._root = cmds.group(ctrl_shapes[0], name=naming.build_name(ctrl_new_name, naming.Names.RootGroup))

        if create_auto_group:
            self._auto = cmds.group(self._root, name=naming.build_name(ctrl_new_name, naming.Names.AutoGroup))
        if create_constraint_group:
            if create_auto_group:
                self._constraint = cmds.group(self._auto, name=naming.build_name(ctrl_new_name, naming.Names.ConstraintGroup))
            else:
                self._constraint = cmds.group(self._root, name=naming.build_name(ctrl_new_name, naming.Names.ConstraintGroup))
        if create_offset_group:
            if create_constraint_group:
                self._offset = cmds.group(self._constraint, name=naming.build_name(ctrl_new_name, naming.Names.OffsetGroup))
            else:
                if create_auto_group:
                    self._offset = cmds.group(self._auto, name=naming.build_name(ctrl_new_name, naming.Names.OffsetGroup))
                else:
                    self._offset = cmds.group(self._root, name=naming.build_name(ctrl_new_name, naming.Names.OffsetGroup))

        target_obj = self._offset if self._offset and sp.dcc.object_exists(self._offset) else ctrl_new_name
        if sp.dcc.object_exists(translate_to):
            sp.dcc.delete_object(cmds.pointConstraint(translate_to, target_obj))
        if sp.dcc.object_exists(rotate_to):
            sp.dcc.delete_objec(cmds.orientConstraint(rotate_to, target_obj))
        if sp.dcc.object_exists(parent):
            sp.dcc.set_parent(target_obj, parent)

        single_attr_lock_list = list()
        for lock_channel in lock_channels:
            if lock_channel in ['t', 'r', 's']:
                for axis in ['x', 'y', 'z']:
                    attr = lock_channel + axis
                    single_attr_lock_list.append(attr)
            else:
                single_attr_lock_list.append(lock_channel)

        for attr in single_attr_lock_list:
            cmds.setAttr('{}.{}'.format(ctrl_new_name, attr), lock=True, keyable=False, channelBox=False)
            # if self._auto:
            #     cmds.setAttr('{}.{}'.format(self._auto, attr, lock=True, keyable=False, channelBox=False))
            # if self._root:
            #     cmds.setAttr('{}.{}'.format(self._root, attr, lock=True, keyable=False, channelBox=False))

        ctrl_shapes = sp.dcc.list_shapes(ctrl_new_name, full_path=True)
        if len(ctrl_shapes) > 1:
            for i in range(len(ctrl_shapes)):
                sp.dcc.rename_node(ctrl_shapes[i], '{}{}Shape'.format(node, naming.get_alpha(i, capital=True)))
        else:
            sp.dcc.rename_node(ctrl_shapes[0], '{}Shape'.format(node))

    @property
    def node(self):
        """
        Returns control node
        :return: str
        """

        return self._node

    @property
    def offset(self):
        """
        Returns offset group
        :return: str
        """

        return self._offset

    @property
    def root(self):
        """
        Returns root node
        :return: str
        """

        return self._root

    @property
    def constraint(self):
        """
        Returns constraint group
        :return: str
        """

        return self._constraint

    @property
    def auto(self):
        """
        Returns auto node
        :return: str
        """

        return self._auto

    def move(self, x, y, z, force_move_node=False):
        """
        Moves control
        :param x: float
        :param y: float
        :param z: float
        """

        if force_move_node:
            cmds.move(x, y, z, self._node)
        else:
            if self._offset:
                cmds.move(x, y, z, self._offset)
            else:
                cmds.move(x, y, z, self._node)

    def get_shapes(self, full_path=True):
        """
        Return all the shapes of a given node where the last parent is the top of hierarchy
        :param full_path: bool
        """

        return sp.dcc.list_shapes(node=self._node, full_path=full_path)

    def get_shapes_components(self):
        """
        Returns shapes components of the MetaNode shapes
        :return: list<str>
        """

        shapes = self.get_shapes(full_path=True)
        return mayautils.get_components_from_shapes(shapes)

    def translate_control_shapes(self, x, y, z):
        """
        Translates the shape curve CVs in object space
        :param x: float
        :param y: float
        :param z: float
        """

        comps = self.get_shapes_components()
        if comps:
            cmds.move(x, y, z, comps, relative=True, os=True)

    def scale_control_shapes(self, x, y=None, z=None):
        """
        Scales shape curve CVs in object space
        :param scale_value: float
        """

        x = x if x != 0 else 1
        y = y if y != 0 else 1
        z = z if z != 0 else 1

        if y is None:
            y = x
        if z is None:
            z = x

        comps = self.get_shapes_components()
        if comps:
            cmds.scale(x, y, z, comps, relative=True, os=True)


class Circle(RigControl, object):
    """
    Class to create circle rig controls
    """

    def __init__(self,  name='circle', normal=[1, 0, 0], radius=1.0, **kwargs):
        super(Circle, self).__init__(node=cmds.circle(name=name, normal=normal, radius=radius, ch=False)[0], **kwargs)