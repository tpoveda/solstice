# -*- coding: utf-8 -*-

"""
Module that contains different utils functions related with Solstice project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import tpDcc as tp

import artellapipe

LOGGER = logging.getLogger()


def get_control(node, rig_control):
    """
    Returns main control of the current asset
    :return: str
    """

    tag_node = artellapipe.TagsMgr().get_tag_node(project=artellapipe.solstice, node=node)
    if not tag_node:
        return None
    asset_node = tag_node.get_asset_node()
    if not asset_node:
        LOGGER.warning('Tag Data node: {} is not linked to any asset! Aborting operation ...'.format(tag_node))
        return
    node_to_apply_xform = asset_node.node
    attrs = tp.Dcc.list_user_attributes(node_to_apply_xform)
    if attrs and type(attrs) == list:
        if rig_control not in attrs:
            all_children = tp.Dcc.list_children(node)
            for child in all_children:
                if child.endswith(rig_control):
                    return child
        else:
            root_ctrl = tp.Dcc.get_attribute_value(node_to_apply_xform, attribute_name=rig_control)
            if not tp.Dcc.object_exists(root_ctrl):
                LOGGER.warning(
                    'Control "{}" does not exists in current scene! Aborting operation...'.format(
                        root_ctrl))
                return None
            return root_ctrl

    return None
