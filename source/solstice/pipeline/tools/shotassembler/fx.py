#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains shot file for FX files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.tools.shotmanager.core import assetitem, shotassembler

import solstice
from solstice.core import defines as solstice_defines


class FXShotFile(assetitem.ShotAssetFileItem, object):

    FILE_TYPE = solstice_defines.SOLSTICE_FX_SHOT_FILE_TYPE
    FILE_ICON = solstice.resource.icon('fx')
    FILE_EXTENSION = solstice_defines.SOLSTICE_FX_EXTENSION

    def __init__(self, asset_file, parent=None):
        super(FXShotFile, self).__init__(asset_file=asset_file, parent=parent)


shotassembler.register_file_type(FXShotFile)
