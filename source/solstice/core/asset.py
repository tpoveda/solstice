#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for asset in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.core import asset as artella_asset


class SolsticeAsset(artella_asset.ArtellaAsset, object):
    def __init__(self, asset_data):
        super(SolsticeAsset, self).__init__(asset_data=asset_data)


class SolsticeAssetWidget(artella_asset.ArtellaAssetWidget, object):
    def __init__(self, asset, parent=None):
        super(SolsticeAssetWidget, self).__init__(asset=asset, parent=parent)
