#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains nomenclature definitions for rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


class Names(object):

    Joint = 'jtn'
    JointEnd = 'jntEnd'
    Group = 'grp'
    Separator = '_'
    Driver = 'grpDrv'
    Locator = 'loc'
    LocatorDriver = 'locDrv'
    Control = 'ctrl'
    OffsetGroup = 'offset'
    AutoGroup = 'auto'
    ConstraintGroup = 'constraint'
    RootGroup = 'root'
    DecomposeMatrix = 'decomposeMatrix'


def build_name(*args):
    return Names.Separator.join(args)


def get_alpha(value, capital=False):
    """
    Returns an alphabetic value from a number. Eg: a-z, aa-zz
    :param value: int, number of a character in the alphabet
    :param capital: bool, Whether if we want the character in capital or not
    :return: str, alphabet character
    """

    base_power = base_start = base_end = 0
    while value >= base_end:
        base_power += 1
        base_start = base_end
        base_end += pow(26, base_power)
    base_index = value - base_start

    alphas = ['a'] * base_power
    for index in range(base_power - 1, -1, -1):
        alphas[index] = chr(97 + (base_index % 26))
        base_index /= 26

    if capital: return ''.join(alphas).upper()
    return ''.join(alphas)


def remove_suffix(name):
    """
    Removes suffix from a string
    :param name: str, name of the string
    :return: str, name without suffix
    """

    edits = name.split(Names.Separator)
    if len(edits) < 2:
        return name

    suffix = Names.Separator + edits[-1]
    name_no_suffix = name[:-len(suffix)]

    return name_no_suffix
