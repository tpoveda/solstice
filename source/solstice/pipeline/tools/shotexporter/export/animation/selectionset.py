#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definition for selection sets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

import solstice.pipeline as sp
from solstice.pipeline.utils import namingutils, exceptions

from solstice.pipeline.tools.shotexporter.export.animation import animobject

if sp.is_maya():
    import maya.cmds as cmds


class SelectionSet(animobject.AnimObject, object):

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        Load/Select the anim objects to the given objects or namespaces
        :param objects: list(str) | None
        :param namespaces: list(str) | None
        :param kwargs:
        """

        valid_nodes = list()
        target_objects = objects
        source_objects = self.objects()

        self.validate(namespaces=namespaces)

        matches = namingutils.match_names(source_objects=source_objects, target_objects=target_objects, target_namespaces=namespaces)

        for source_node, target_node in matches:
            if '*' in target_node.name():
                valid_nodes.append(target_node.name())
            else:
                target_node.strip_first_pipe()

            try:
                target_node = target_node.to_short_name()
            except exceptions.NoObjectFoundError as e:
                sys.solstice.logger.error(e)
                continue
            except exceptions.MoreThanOneObjectFoundError as e:
                sys.solstice.logger.error(e)

            valid_nodes.append(target_node.name())

        if valid_nodes:
            sys.solstice.dcc.select_object(valid_nodes, **kwargs)
            if sp.is_maya():
                cmds.setFocus('MayaWindow')
        else:
            msg = 'No objects match when loading data.'
            raise exceptions.NoMatchFoundError(msg)

    def select(self, objects=None, namespaces=None, **kwargs):
        """
        Function to select SelectionSets
        :param objects: str
        :param namespaces: list(str)
        :param kwargs:
        """

        SelectionSet.load(self, objects=objects, namespaces=namespaces, **kwargs)


def save_selection_set(path, objects, metadata=None):
    """
    Function for saving a selection set to the given disk path
    :param path: str
    :param objects: list(str)
    :param metadata: dict | None
    :return:
    """

    selection_set = SelectionSet.from_objects(objects)
    if metadata:
        selection_set.update_metadata(metadata)
    selection_set.save(path)

    return selection_set
