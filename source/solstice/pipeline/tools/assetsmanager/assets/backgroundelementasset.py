#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for background element assets in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from solstice.core import asset


class BackgroundElementAsset(asset.SolsticeAssetWidget, object):
    def __init__(self, asset, parent=None):
        super(BackgroundElementAsset, self).__init__(asset=asset, parent=parent)
