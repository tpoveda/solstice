#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget implementation for asset viewer for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


from artellapipe.core import assetsviewer

from solstice.core import asset


class SolsticeAssetsViewer(assetsviewer.AssetsViewer, object):

    ASSET_WIDGET_CLASS = asset.SolsticeAssetWidget

    def __init__(self, project, column_count=3, parent=None):
        super(SolsticeAssetsViewer, self).__init__(project=project, column_count=column_count, parent=parent)
