#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definition for attributes
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

import solstice.pipeline as sp

if sp.is_maya():
    import maya.cmds as cmds


VALID_CONNECTIONS = [
    "animCurve",
    "animBlend",
    "pairBlend",
    "character"
]

VALID_BLEND_ATTRIBUTES = [
    "int",
    "long",
    "float",
    "short",
    "double",
    "doubleAngle",
    "doubleLinear",
]

VALID_ATTRIBUTE_TYPES = [
    "int",
    "long",
    "enum",
    "bool",
    "string",
    "float",
    "short",
    "double",
    "doubleAngle",
    "doubleLinear",
]


class AttributeError(Exception):
    """
    Base class for attribute exceptions
    """

    pass


class Attribute(object):
    def __init__(self, name, attr=None, value=None, attr_type=None, cache=True):
        """
        :param name: str
        :param attr: str | None
        :param value: str | None
        :param attr_type: object | None
        :param cache: bool
        """

        if '.' in name:
            name, attr = name.split('.')

        if attr is None:
            msg = 'Cannot initialize attribute instance without a given attribute'
            raise AttributeError(msg)

        try:
            self._name = name.encode('ascii')
            self._attr = name.encode('ascii')
        except UnicodeEncodeError:
            msg = 'Not a valid ASCII name "{}.{}"'.format(name, attr)
            raise UnicodeEncodeError(msg)

        self._type = attr_type
        self._value = value
        self._cache = cache
        self._fullname = None

    def __str__(self):
        return str(self.to_dict())

    def name(self):
        """
        Returns the full name of the attribute
        :return: str
        """

        return self._name

    def attr(self):
        """
        Returns the name of the attribute
        :return: str
        """

        return self._attr

    def is_locked(self):
        """
        Returns whether attribute is locked or not
        :return: bool
        """

        node, attr_name = self.fullname().split('.')
        return sys.solstice.dcc.is_attribute_locked(node=node, attribute_name=attr_name)

    def is_unlocked(self):
        """
        Returns whether attribute is unlocked or not
        :return: bool
        """

        return not self.is_locked()

    def to_dict(self):
        """
        Returns a dictionary of the attribute
        :return: dict
        """

        result = {
            'type': self.attribute_type(),
            'value': self.value(),
            'fullname': self.fullname()
        }

        return result

    def is_valid(self):
        """
        Returns whether the attribute is valid or not
        :return: bool
        """

        return self.attribute_type() in VALID_ATTRIBUTE_TYPES

    def exists(self):
        """
        Returns whether attribute exists or not
        :return: bool
        """

        return sys.solstice.dcc.object_exists(self.fullname())

    def pretty_print(self):
        """
        Print the command for setting the attribute name
        """

        msg = 'maya.cmds.getAttr("{}", "{}")'.format(self.fullname(), self.value())
        print(msg)

    def clear_cache(self):
        """
        Clear all cached values
        """

        self._type = None
        self._value = None

    def query(self, **kwargs):
        """
        Function for query for attributes
        :param kwargs:
        :return: variant
        """

        node, _ = self.fullname().split('.')
        return sys.solstice.dcc.attribute_query(node=self.name(), attribute_name=self.attr(), **kwargs)

    def list_connections(self, **kwargs):
        """
        Returns list of attribute connections
        :return: list(str)
        """

        if sp.is_maya():
            return cmds.listConnections(self.fullname(), **kwargs)

        return list()

    def source_connection(self, **kwargs):
        """
        Returns the source connection for this attribute
        :param kwargs:
        :return: str | None
        """

        try:
            return self.list_connections(destination=False, **kwargs)[0]
        except IndexError:
            return None

    def fullname(self):
        """
        Returns the name with the attribute name
        :return: str
        """

        if self._fullname is None:
            self._fullname = '{}.{}'.format(self.name(), self.attr())

        return self._fullname

    def value(self):
        """
        Returns the value of the attribute
        :return: float | str | list
        """

        if self._value is None or not self._cache:
            try:
                self._value = sys.solstice.dcc.get_attribute_value(node=self.name(), attribute_name=self.attr())
            except Exception:
                msg = 'Cannot get attribute value for "{}"'.format(self.fullname())
                sys.solstice.logger.error(msg)

        return self._value

    def attribute_type(self):
        """
        Returns the type of data currently in the attribute
        :return: str
        """

        if self._type is None:
            try:
                self._type = sys.solstice.dcc.get_attribute_type(node=self.name(), attribut_name=self.attr())
                self._type = self._type.encode('ascii')
            except Exception:
                msg = 'Cannot get attribute type for "{}"'.format(self.fullname())
                sys.solstice.logger.error(msg)

        return self._type

    def set_value(self, value, blend=100, key=False, clamp=True):
        """
        Stes the value for the attribute
        :param value: float | str | list
        :param blend: float
        :param key: bool
        :param clamp: bool
        """

        try:
            if int(blend) == 0:
                value = self.value()
            else:
                _value = (value - self.value()) * (blend/100.0)
                value = self.value() + _value
        except TypeError as e:
            msg = 'Cannot blend attribute {}: Error: {}'.format(self.fullname(), e)
            sys.solstice.logger.error(msg)

        try:
            if self.attribute_type() in ['string']:
                sys.solstice.dcc.set_attribute_by_type(node=self.name(), attribute_name=self.attr(), attribute_value=value, attribute_type=self.attribute_type())
            elif self.attribute_type() in ['list', 'matrix']:
                if sp.is_maya():
                    cmds.setAttr(self.fullname(), *value, type=self.attribute_type())
            else:
                sys.solstice.dcc.set_numeric_attribute_value(node=node, attribute_name=attr_name, attribute_value=value, clamp=clamp)
        except (ValueError, RuntimeError) as e:
            msg = 'Cannot set attribute {}: Error: {}'.format(self.fullname(), e)
            sys.solstice.logger.error(msg)

        try:
            if key:
                self.set_key_frame(value=value)
        except TypeError as e:
            msg = 'Cannot key asttribute {}: Error: {}'.format(self.fullname(), e)
            sys.solstice.logger.error(msg)

    def set_key_frame(self, value, respect_keyable=True, **kwargs):
        """
        Sets a keyframe with the given value
        :param value: object
        :param respect_keyable: bool
        :param kwargs:
        """

        if self.query(minExists=True):
            minimum = self.query(minimum=True)[0]
            if value < minimum:
                value = minimum
            if self.query(maxExists=True):
                maximum = self.query(maximum=True)[0]
                if value > maximum:
                    value = maximum

        kwargs.setdefault('value', value)
        kwargs.setdefault('respectKeyable', respect_keyable)

        sys.solstice.dcc.set_key_framert(node=self.name(), attribute_name=self.attr(), **kwargs)

    def set_static_key_frame(self, value, time, option):
        """
        Sts a static keyframe at the given time
        :param value: object
        :param time: (int, int)
        :param option: PasteOption
        """

        if option == 'replaceCompletely':
            sys.solstice.dcc.cut_key(node=self.name(), attribute_name=self.attr())
            self.set_value(value=value, key=False)
        elif self.is_connected():
            # TODO: Should also support static attrs when there is animation.
            if option == 'replace':
                sys.solstice.dcc.cut_key(node=self.name(), attribute_name=self.attr(), time=time)
                self.insert_static_key_frame(value, time)
        else:
            self.set_value(value=value, key=False)

    def insert_static_key_frame(self, value, time):
        """
        Inserts a static keyframe at the given time with the given value
        :param value: float | str
        :param time: (int, int)
        """

        start_time, end_time = time
        duration = end_time - start_time

        try:
            sys.solstice.dcc.offset_keyframes(node=self.name(), attribute_name=self.attr(), start_time=start_time, end_time=1000000, duration=duration)
            self.set_key_frame(value=value, time=(start_time, start_time), ott='step')
            self.set_key_frame(value=value, time=(end_time, end_time), itt='flat', ott='flat')
            next_frame = sys.solstice.dcc.find_next_key_frame(node=self.name(), attribute_name=self.attr(), start_time=end_time, end_time=end_time)
            sys.solstice.dcc.set_flat_key_frame(node=self.name(), attribute_name=self.attr(), start_time=next_frame, end_time=next_frame)
        except TypeError as e:
            msg = 'Cannot insert static key frame for attribute {}: Error: {}'.format(self.fullname(), e)
            sys.solstice.logger.error(msg)

    def set_anim_curve(self, curve, time, option, source=None, connect=False):
        """
        Set/Paste the given animation curve to this attribute
        :param curve: str
        :param time: (int, int)
        :param option: PasteOption
        :param source: (int, int)
        :param connect: bool
        """

        fullname = self.fullname()
        start_time, end_time = time

        if source is None:
            source = (None, None)

        if not self.exists():
            sys.solstice.logger.warning('Attr {} does not exists!'.format(self.fullname()))
            return
        if self.is_locked():
            sys.solstice.logger.warning('Attribute {} is locked! Cannot set anim curve when the attribute is locked!'.format(self.fullname()))
            return

        if source is None:
            first = sys.solstice.dcc.find_first_key_in_anim_curve(curve)
            last = sys.solstice.dcc.find_last_key_in_anim_curve(curve)
            source = (first, last)

        success = sys.solstice.dcc.copy_anim_curve(curve=curve, start_time=source[0], end_time=source[1])
        if not success:
            msg = 'Cannot copy keys from the animation curve {}'.format(curve)
            sys.solstice.logger.error(msg)
            return

        if option == 'replace':
            sys.solstice.dcc.cut_key(node=self.name(), attribute_name=self.attr(), time=time)
        else:
            time = (start_time, end_time)

        try:
            sys.solstice.dcc.copy_key(node=self.name(), attribute_name=self.attr(), time=source)
            sys.solstice.dcc.paste_key(node=self.name(), attribute_name=self.attr(), option=option, time=time, connect=connect)
            if option == 'replaceCompletely':
                target_curve = self.anim_curve()
                if target_curve:
                    curve_color = sys.solstice.dcc.get_attribute_value(node=curve, attribute_name='curveColor')
                    pre_infinity = sys.solstice.dcc.get_attribute_value(node=curve, attribute_name='preInfinity')
                    post_infinity = sys.solstice.dcc.get_attribute_value(node=curve, attribute_name='postInfinity')
                    use_curve_color = sys.solstice.dcc.get_attribute_value(node=curve, attribute_name='useCurveColor')
                    sys.solstice.dcc.set_numeric_attribute_value(node=curve, attribute_name='preInfinity', attribute_value=pre_infinity)
                    sys.solstice.dcc.set_numeric_attribute_value(node=curve, attribute_name='postInfinity', attribute_value=post_infinity)
                    sys.solstice.dcc.set_numeric_attribute_value(node=curve, attribute_name='curveColor', attribute_value=curve_color)
                    sys.solstice.dcc.set_numeric_attribute_value(node=curve, attribute_name='useCurveColor', attribute_value=use_curve_color)
        except RuntimeError:
            msg = 'Cannot paste anim curve "{}" to attribute "{}"'.format(curve, fullname)
            sys.solstice.logger.error(msg)

    def anim_curve(self):
        """
        Returns the connected animation curve
        :return: str | None
        """

        if not sp.is_maya():
            sys.solstice.logger.warning('Animation Curves are only supported in Maya!')
            return

        result = None

        if self.exists():
            n = self.list_connections(plugs=True, destination=True)
            if n and 'animCurve' in sys.solstice.dcc.node_type(n):
                result = n
            elif n and 'character' in sys.solstice.dcc.node_type(n):
                n = self.list_connections(n, plugs=True, destination=False)
                if n and 'animCurve' in sys.solstice.dcc.node_type(n):
                    result = n

            if result:
                return result[0].split('.')[0]

    def is_connected(self, ignore_connections=None):
        """
        Returns True if the attribute is connected
        :param ignore_connections: list(str)
        :return: bool
        """

        if ignore_connections is None:
            ignore_connections = list()

        try:
            connection = self.list_connections(destination=False)
        except ValueError:
            return False

        if connection:
            if ignore_connections:
                connection_type = sys.solstice.dcc.node_type(connection)
                for ignore_type in ignore_connections:
                    if connection_type.startswith(ignore_type):
                        return False
            return True
        else:
            return False

    def is_blendable(self):
        """
        Returns True if the attribute can be blended
        :return: bool
        """

        return self.attribute_type() in VALID_BLEND_ATTRIBUTES

    def is_settable(self, valid_connections=None):
        """
        Returns True if the attribute can be set
        :param valid_connections: list(str)
        :return: bool
        """

        if valid_connections is None:
            valid_connections = VALID_CONNECTIONS

        if not self.exists():
            return False

        if not sys.solstice.dcc.list_attributes(node=self.fullname(), unlocked=True, keyable=True, multi=True, scalar=True):
            return False

        connection = self.list_connections(destination=True)
        if connection:
            connection_type = sys.solstice.dcc.node_type(connection)
            for valid_type in valid_connections:
                if connection_type.startswith(valid_type):
                    return True
            return False
        else:
            return True
