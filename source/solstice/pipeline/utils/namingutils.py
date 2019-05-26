#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities functions relating with naming
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys

import solstice.pipeline as sp

if sp.is_maya():
    import maya.cmds as cmds


def get_alpha(value, capital=False):
    """
    Convert an integer value to a character. a-z then double, aa-zz etc.
    @param value: int, Value to get an alphabetic character from
    @param capital: boolean: True if you want to get capital character
    @return: str, Character from an integer
    """

    # Calculate number of characters required
    base_power = base_start = base_end = 0
    while value >= base_end:
        base_power += 1
        base_start = base_end
        base_end += pow(26, base_power)
    base_index = value - base_start

    # Create alpha representation
    alphas = ['a'] * base_power
    for index in range(base_power - 1, -1, -1):
        alphas[index] = chr(97 + (base_index % 26))
        base_index /= 26

    if capital:
        return ''.join(alphas).upper()

    return ''.join(alphas)


def find_available_name(name, suffix='', index=0, padding=0, letters=False, capital=False):
    """
    Recursively find a free name matching specified criteria
    @param name: str, Name to check if already exists in the scene
    @param suffix: str, Suffix for the name
    @param index: int, Index of the name
    @param padding: int, Padding for the characters/numbers
    @param letters: bool, True if we want to use letters when renaming multiple nodes
    @param capital: bool, True if we want letters to be capital
    """

    test_name = name

    if letters is True:
        letter = get_alpha(index - 1, capital)
        test_name = '%s_%s' % (name, letter)
    else:
        test_name = '%s_%s' % (name, str(index).zfill(padding + 1))

    if suffix:
        test_name = '%s_%s' % (test_name, suffix)

    # if object exists, try next index
    if cmds.objExists(test_name):
        return find_available_name(name, suffix, index + 1, padding, letters, capital)

    return test_name


def format_path(path):
    """
    Takes a path and format it to forward slashes
    :param path: str
    :return: str
    """

    return os.path.normpath(path).replace('\\', '/').replace('\t', '/t').replace('\n', '/n').replace('\a', '/a')


def rotate_sequence(seq, current):
    """
    Returns proper rotate sequence naming
    :param seq: str
    :param current: str
    :return: str
    """

    n = len(seq)
    for i in range(n):
        yield seq[(i + current) % n]


def group_objects(objects):
    """
    Returns objects as SolsticeNodes
    :param objects: list(str)
    :return: dict
    """

    results = dict()
    for name in objects:
        node = sp.Node(name)
        results.setdefault(node.namespace(), [])
        results[node.namespace()].append(name)

    return results


def index_objects(objects):
    """
    Returns objects indices
    :param objects: list(str)
    :return: dict
    """

    result = dict()
    if objects:
        for name in objects:
            node = sp.Node(name)
            result.setdefault(node.short_name(), [])
            result[node.short_name()].append(node)

    return result


def match_in_index(node, index):
    """
    Match objects index
    :param node: SolsticeNodeDCC
    :param index: int
    :return: list
    """

    result = None
    if node.short_name() in index:
        nodes = index[node.short_name()]
        if nodes:
            for n in nodes:
                if node.name().endswith(n.name()) or n.name().endswith(node.name()):
                    result = n
                    break
        if result is not None:
            index[node.short_name()].remove(result)

    return result


def match_names(source_objects, target_objects=None, target_namespaces=None, search=None, replace=None):
    """
    Checks if source and target objects matches
    :param source_objects: list(str)
    :param target_objects: list(str)
    :param target_namespaces: list(str)
    :param search: bool
    :param replace: bool
    :return: list(SolsticeNodeDCC, SolsticeNodeDCC)
    """

    results = list()
    if target_objects is None:
        target_objects = list()

    source_group = group_objects(source_objects)
    source_namespaces = source_group.keys()

    if not target_objects and not target_namespaces:
        target_namespaces = source_namespaces
    if not target_namespaces and target_objects:
        target_group = group_objects(target_objects)
        target_namespaces = target_group.keys()

    target_index = index_objects(target_objects)
    target_namespaces2 = list(set(target_namespaces) - set(source_namespaces))
    target_namespaces1 = list(set(target_namespaces) - set(target_namespaces2))

    used_namespaces = list()
    not_used_namespaces = list()

    for source_namespace in source_namespaces:
        if source_namespace in target_namespaces1:
            used_namespaces.append(source_namespace)
            for name in source_group[source_namespace]:
                source_node = sp.Node(name)
                if search is not None and replace is not None:
                    name = name.replace(search, replace)
                target_node = sp.Node(name)
                if target_objects:
                    target_node = match_in_index(target_node, target_index)
                if target_node:
                    results.append((source_node, target_node))
                    yield (source_node, target_node)
                else:
                    sys.solstice.logger.warning('Cannot find matching target object for {}'.format(source_node.name()))
        else:
            not_used_namespaces.append(source_namespace)

    source_namespaces = not_used_namespaces
    source_namespaces.extend(used_namespaces)
    _index = 0
    for target_namespace in target_namespaces2:
        match = False
        i = _index
        for source_namespace in rotate_sequence(source_namespaces, _index):
            if match:
                _index = i
                break
            i += 1
            for name in source_group[source_namespace]:
                source_node = sp.Node(name)
                target_node = sp.Node(name)
                target_node.set_namespace(target_namespace)
                if target_objects:
                    target_node = match_in_index(target_node, target_index)
                elif target_namespaces:
                    pass
                if target_node:
                    match = True
                    results.append((source_node, target_node))
                    yield (source_node, target_node)
                else:
                    sys.solstice.logger.warning('Cannot find matching target object for {}'.format(source_node.name()))

    for target_nodes in target_index.values():
        for target_node in target_nodes:
            sys.solstice.logger.debug('Cannot find matching ')
