#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definitions for DCC nodes in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.core import node


class SolsticeAssetNode(node.ArtellaAssetNode, object):
    def __init__(self, project, node=None, **kwargs):
        super(SolsticeAssetNode, self).__init__(project=project, node=node, **kwargs)