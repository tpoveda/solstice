#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful decorators
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import time

import solstice.pipeline as sp


def empty(fn):
    """
    Empty decorator
    :param fn:
    :return: wrapped function
    """

    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def timing(fn):
    """
    Simple decorator to calculates how much time an operation costs in seconds
    :param fn:
    :return: wrapped function
    """

    def wrapper(*args, **kwargs):
        time1 = time.time()
        ret = fn(*args, **kwargs)
        time2 = time.time()
        sp.logger.debug('%s function took %0.5f sec' % (fn.func_name, (time2 - time1)))
        return ret
    return wrapper
