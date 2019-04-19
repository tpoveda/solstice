#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exceptions definitions
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"


class SolsticeError(Exception, object):
    """
    Base class for Solstice Exceptions
    """

    pass


class NoObjectFoundError(SolsticeError, object):
    pass


class MoreThanOneObjectFoundError(SolsticeError, object):
    pass


class NoMatchFoundError(SolsticeError, object):
    pass