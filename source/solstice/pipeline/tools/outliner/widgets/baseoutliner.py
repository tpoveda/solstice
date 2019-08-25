#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains different outliners for Solstice Outliner
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.tools.outliner.widgets import baseoutliner

from solstice.pipeline.tools.outliner.items import base


class SolsticeBaseOutliner(baseoutliner.BaseOutliner, object):

    OUTLINER_ITEM = base.SolsticeOutlinerAssetItem

    def __init__(self, project, parent=None):
        super(SolsticeBaseOutliner, self).__init__(project=project, parent=parent)

