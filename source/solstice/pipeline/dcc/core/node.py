#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains abstract definition of basic DCC node functions
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.utils import exceptions


class SolsticeNodeDCC(object):

    def __init__(self, name, attributes=None):
        try:
            self._name = name.encode('ascii')
        except UnicodeEncodeError:
            raise UnicodeEncodeError('Not a valid ASCII name "{}"'.format(name))

        self._short_name = None
        self._namespace = None
        self._mirror_axis = None
        self._attributes = attributes

    def __str__(self):
        return self.name()

    def name(self):
        """
        Returns name
        :return: str
        """

        return self._name

    def attributes(self):
        """
        Returns list of node attributes
        :return: str
        """

        return self._attributes

    def short_name(self):
        """
        Returns node short name
        :return: str
        """

        import solstice.pipeline as sp
        if self._short_name is None:
            self._short_name = sp.dcc.node_short_name(self.name())

        return self._short_name

    def namespace(self):
        """
        Returns node namespace
        :return: str
        """

        if self._namespace is None:
            self._namespace = ':'.join(self.short_name().split(':')[:-1])

        return self._namespace

    def set_mirror_axis(self, mirror_axis):
        """
        Set the mirror axis
        :param mirror_axis: str
        """

        self._mirror_axis = mirror_axis

    def set_namespace(self, namespace):
        """
        Sets the namespace for current node in Maya
        :param namespace: str
        """

        new_name = self.name()
        old_name = self.name()
        new_namespace = namespace
        old_namespace = self.namespace()

        if new_namespace == old_namespace:
            return self.name()

        if old_namespace and new_namespace:
            new_name = old_name.replace(old_namespace + ':', new_namespace + ':')
        elif old_namespace and not new_namespace:
            new_name = old_name.replace(old_namespace + ':', '')
        elif not old_namespace and new_namespace:
            new_name = old_name.replace('|', '|' + new_namespace + ':')
            if new_namespace and not new_name.startswith('|'):
                new_name = new_namespace + ':' + new_name

        self._name = new_name
        self._short_name = None
        self._namespace = None

        return self.name()

    @classmethod
    def selected_nodes(cls, objects=None, selection=False):
        """
        Returns a list of SolsticeNodeDCC nodes
        :param objects: list(str)
        :param selection: bool
        :return: list(SolsticeNodeDCC)
        """

        import solstice.pipeline as sp

        if object is None and not selection:
            objects = sp.dcc.list_nodes()
        else:
            objects = objects or []
            if selection:
                objects.extend(sp.dcc.selected_nodes(full_path=False) or [])

        return [cls(name) for name in objects]

    def to_short_name(self):
        """
        Converts current name to short name
        :return: str
        """

        import solstice.pipeline as sp

        names = sp.dcc.list_nodes(node_name=self.short_name())
        if len(names) == 1:
            return SolsticeNodeDCC(names[0])
        elif len(names) > 1:
            raise exceptions.MoreThanOneObjectFoundError('More than one object found {}'.format(str(names)))
        else:
            raise exceptions.NoObjectFoundError('No object found {}'.format(self.short_name()))

    def strip_first_pipe(self):
        """
        Removes first strip from node name
        :return: str
        """

        if self.name().startswith('|'):
            self._name = self.name()[1:]

    def exists(self):
        """
        Returns whether node exists or not
        :return: bool
        """

        import solstice.pipeline as sp

        return sp.dcc.object_exists(self.name())

    def is_long(self):
        """
        Returns whether node name is long or not
        :return: bool
        """

        return '|' in self.name()

    def is_referenced(self):
        """
        Returns whether node is referenced or not
        :return: bool
        """

        import solstice.pipeline as sp

        return sp.dcc.node_is_referenced(self.name())
