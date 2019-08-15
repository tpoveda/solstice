#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow to manage scene assets for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDccLib as tp

import artellapipe
from artellapipe.gui import window
from artellapipe.tools.outliner import outliner


class SolsticeOutlinerWidget(outliner.ArtellaOutlinerWidget, object):

    title = 'Solstice - Outliner'

    def __init__(self, project, parent=None):
        super(SolsticeOutlinerWidget, self).__init__(project=project, parent=parent)

    def _create_outliners(self):
        """
        Overrides base ArtellaOutlinerWidget _create_outliners function
        Updates current tag categories with the given ones
        :param outliner_categories: list(str)
        """

        from solstice.pipeline.tools.outliner.outliners import assetsoutliner

        assets_outliner = assetsoutliner.SolsticeAssetsOutliner(project=self._project)

        self.add_outliner(assets_outliner)


class SolsticeOutliner(outliner.ArtellaOutliner, object):
    def __init__(self, project, parent=None):
        super(SolsticeOutliner, self).__init__(project=project, parent=parent)


def run():
    if tp.is_maya():
        win = window.dock_window(project=artellapipe.solstice, window_class=SolsticeOutlinerWidget)
        return win
    else:
        win = SolsticeOutliner(project=artellapipe.solstice)
        win.show()
        return win
