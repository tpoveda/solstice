#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow artists to interact with Artella functionality inside DCCS in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from artellapipe.tools.assetsmanager.core import assetsmanager

from solstice.pipeline.tools.assetsmanager.widgets import assetswidgets


class SolsticeAssetsManager(assetsmanager.ArtellaAssetsManager, object):

    ASSET_WIDGET_CLASS = assetswidgets.PlotTwistAssetsWidget

    def __init__(self):
        super(SolsticeAssetsManager, self).__init__(
            project=artellapipe.solstice, auto_start_assets_viewer=True
        )


def run():
    win = SolsticeAssetsManager()
    win.show()

    return win
