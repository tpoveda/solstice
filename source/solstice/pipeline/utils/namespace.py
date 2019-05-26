#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functionality to handle namespaces
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


def get_from_dag_path(dag_path):
    """
    Returns namespace from given DAG path
    :param dag_path: str
    :return: str
    """

    short_name = dag_path.split('|')[-1]
    namespace = ':'.join(short_name.split(':')[:-1])

    return namespace


def get_from_dag_paths(dag_paths):
    """
    Returns namespaces from DAG paths
    :param dag_paths: list(str)
    :return: list(str)
    """

    namespaces = list()
    for dag_path in dag_paths:
        namespace = get_from_dag_path(dag_path)
        namespaces.append(namespace)

    return list(set(namespaces))


def get_from_selection():
    """
    Returns namespaces from selected objects
    :return: list(str)
    """

    dag_paths = sys.solstice.dcc.selected_nodes(full_path=False)

    return get_from_dag_paths(dag_paths)


def get_all():
    """
    Returns all available namespaces in the current scene
    :return: list(str)
    """

    if not sp.is_maya():
        return list()

    IGNORE_NAMESPACES = ['UI', 'shared']
    namespaces = sorted(list(set(cmds.namespaceInfo(listOnlyNamespaces=True)) - set(IGNORE_NAMESPACES)))

    return namespaces



