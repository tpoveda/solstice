#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Artella project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from artellapipe.core import project as artella_project

from solstice.core import asset, node


class Solstice(artella_project.ArtellaProject, object):

    ASSET_CLASS = asset.SolsticeAsset
    ASSET_NODE_CLASS = node.SolsticeAssetNode
    TAG_NODE_CLASS = asset.SolsticeTagNode

    def __init__(self):
        super(Solstice, self).__init__(name='Solstice')
