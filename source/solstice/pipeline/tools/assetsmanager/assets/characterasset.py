#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for character assets in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from solstice.core import asset


class CharacterAsset(asset.SolsticeAssetWidget, object):
    def __init__(self, asset, parent=None):
        super(CharacterAsset, self).__init__(asset=asset, parent=parent)


# artellapipe.solstice.register_asset(CharacterAsset)
