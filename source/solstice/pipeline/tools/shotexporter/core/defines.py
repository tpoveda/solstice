#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains constants for Solstice ShotExporter Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


MUST_ATTRS = [
    'worldMatrix',
    'translateX', 'translateY', 'translateZ',
    'rotateX', 'rotateY', 'rotateZ',
    'scaleX', 'scaleY', 'scaleZ']

ABC_ATTRS = [
    'speed', 'offset', 'abc_file', 'time', 'startFrame', 'endFrame', 'cycleType'
]