#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget implementation for assets manager widget for Plot Twist
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.tools.assetsmanager.widgets import assetswidget

from solstice.core import assetsviewer


class PlotTwistAssetsWidget(assetswidget.AssetsWidget, object):

    ASSETS_VIEWER_CLASS = assetsviewer.SolsticeAssetsViewer

    def __init__(self, project, parent=None):
        super(PlotTwistAssetsWidget, self).__init__(project=project, parent=parent)
