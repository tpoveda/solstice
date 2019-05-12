#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class to create prop rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

from solstice.pipeline.tools.autorigger.core import rig
reload(rig)


class PropRig(rig.AssetRig):
    """
    Class to create prop/background elements rigs
    """

    def __init__(self, asset):
        super(PropRig, self).__init__(asset=asset)
