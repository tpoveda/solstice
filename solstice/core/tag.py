#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for tags in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import ast
import logging

import tpDccLib as tp
from tpPyUtils import python

import artellapipe.register
from artellapipe.core import tag

LOGGER = logging.getLogger()


class SolsticeTagNode(tag.ArtellaTagNode, object):
    def __init__(self, project, node, tag_info=None):
        super(SolsticeTagNode, self).__init__(project=project, node=node, tag_info=tag_info)

    def get_types(self):
        """
        Returns a list of types for the current asset
        :return: list(str)
        """

        return python.force_list(self._get_attribute('types'))

    def get_proxy_group(self):
        """
        Returns proxy group linked to tag node
        :return: str
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            return self._node
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='proxy'):
                return None

            connections = tp.Dcc.list_connections(node=self._node, attribute_name='proxy')
            if connections:
                node = connections[0]
                if tp.Dcc.object_exists(node):
                    return node

        return None

    def get_hires_group(self):
        """
        Returns hires group linked to tag node
        :return: str
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            return self._node
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='hires'):
                return None

            connections = tp.Dcc.list_connections(node=self._node, attribute_name='hires')
            if connections:
                node = connections[0]
                if tp.Dcc.object_exists(node):
                    return node

        return None

    def get_shaders(self):
        """
        Returns shaders info linked to this node
        :return: dict
        """

        if not self._node or not tp.Dcc.object_exists(self._node):
            return None

        if self._tag_info_dict:
            shaders_info = self._tag_info_dict.get('shaders', None)
            if not shaders_info:
                LOGGER.warning('Impossible retrieve shaders info of node: {}'.format(self._node))
                return
            shaders_info_fixed = shaders_info.replace("'", "\"")
            shaders_dict = ast.literal_eval(shaders_info_fixed)
            if type(shaders_dict) != dict:
                LOGGER.error(
                    'Impossible to get dictionary from shaders info. Maybe shaders are not set up properly. '
                    'Please contact TD!')
            else:
                return shaders_dict
        else:
            if not tp.Dcc.attribute_exists(node=self._node, attribute_name='shaders'):
                return None

            shaders_attr = tp.Dcc.get_attribute_value(node=self._node, attribute_name='shaders')
            shaders_attr_fixed = shaders_attr.replace("'", "\"")
            shaders_dict = ast.literal_eval(shaders_attr_fixed)
            if type(shaders_dict) != dict:
                LOGGER.error(
                    'Impossible to get dictionary from shaders attribute. Maybe shaders are not set up properly. '
                    'Please contact TD!')
            else:
                return shaders_dict

            return shaders_attr

        return None


artellapipe.register.register_class('TagNode', SolsticeTagNode)
