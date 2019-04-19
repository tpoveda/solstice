#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class for exporter widgets
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.utils import attribute

from solstice.pipeline.tools.shotexporter.export.animation import animobject, selectionset

if sp.is_maya():
    import maya.cmds as cmds


class Pose(animobject.AnimObject, object):
    def __init__(self):
        super(Pose, self).__init__()

        self._cache = None
        self._mtime = None
        self._cache_key = None
        self._is_loading = False
        self._selection = None
        self._mirror_table = None
        self._auto_key_frame = None

    def create_object_data(self, name):
        """
        Creates the object data for the given object name
        :param name: str
        :return: dict
        """

        attrs = cmds.listAttr(name, unlocked=True, keyable=True) or []
        attrs = list(set(attrs))
        attrs = [attribute.Attribute(name=name, attr=attr) for attr in attrs]

        data = {'attrs': self.attrs(name)}

        for attr in attrs:
            if attr.is_valid():
                if attr.value() is None:
                    msg = 'Cannot save the attribute {} with value None'
                    sp.logger.warning(msg, attr.fullname())
                else:
                    data['attrs'][attr.attr()] = {
                        'type': attr.attribute_type(),
                        'value': attr.value()
                    }

        return data

    def select(self, objects=None, namespaces=None, **kwargs):
        """
        Selects the objects contained in the pose file
        :param objects: list(str) | None
        :param namespaces: list(str) | None
        """

        selection_set = selectionset.SelectionSet.from_path(self.path())
        selection_set.load(objects=objects, namespaces=namespaces, **kwargs)

    def cache(self):
        """
        Returns the current cached attributes for the pose
        :return: list(Attribute, Attribute)
        """

        return self._cache

    def attrs(self, name):
        """
        Returns the attribute for the given name
        :param name: str
        :return: dict
        """

        return self.object(name).get('attrs', {})

    def attr(self, name, attr):
        """
        Returns the attribute data for the given name and attribute
        :param name: str
        :param attr: str
        :return: str
        """

        return self.attr(name, attr).get('type', None)

    def attr_type(self, name, attr):
        """
        Returns the attribute type for the given name and attribute
        :param name: str
        :param attr: str
        :return: str
        """

        return self.attr(name, attr).get('type', None)

    def attr_value(self, name, attr):
        """
        Returns the attribute value for the given name and attribute
        :param name: str
        :param attr: str
        :return: str | int | float
        """

        return self.attr(name, attr).get('value', None)
