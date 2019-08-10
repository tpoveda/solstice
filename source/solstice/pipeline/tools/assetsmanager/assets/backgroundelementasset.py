#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for prop assets in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe

from solstice.core import defines, asset


class SolsticeBackgroundElementAsset(asset.SolsticeAsset, object):

    ASSET_TYPE = defines.SOLSTICE_BACKGROUND_ELEMENTS_ASSETS
    ASSET_FILES = {
        defines.SOLSTICE_TEXTURES_ASSET_TYPE: artellapipe.resource.icon(defines.SOLSTICE_TEXTURES_ASSET_TYPE),
        defines.SOLSTICE_MODEL_ASSET_TYPE: artellapipe.resource.icon(defines.SOLSTICE_MODEL_ASSET_TYPE),
        defines.SOLSTICE_SHADING_ASSET_TYPE: artellapipe.resource.icon(defines.SOLSTICE_SHADING_ASSET_TYPE),
        defines.SOLSTICE_RIG_ASSET_TYPE: artellapipe.resource.icon(defines.SOLSTICE_RIG_ASSET_TYPE)
    }

    def __init__(self, project, asset_data):
        super(SolsticeBackgroundElementAsset, self).__init__(project=project, asset_data=asset_data)
