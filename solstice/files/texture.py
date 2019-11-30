#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for texture asset files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.core import assetfile


class SolsticeTextureAssetFile(assetfile.ArtellaAssetFile, object):
    def __init__(self, asset=None):
        super(SolsticeTextureAssetFile, self).__init__(file_asset=asset)
