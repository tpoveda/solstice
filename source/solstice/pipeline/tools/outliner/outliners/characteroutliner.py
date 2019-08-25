#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for characters outliner
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from solstice.pipeline.tools.outliner.widgets import baseoutliner


class SolsticeCharactersOutliner(baseoutliner.SolsticeBaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeCharactersOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['character']
