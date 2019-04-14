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
