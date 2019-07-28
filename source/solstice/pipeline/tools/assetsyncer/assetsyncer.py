#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool used to synchronize all assets to its latest available versions
ç"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.gui import window
from solstice.pipeline.utils import decorators, outliner as utils

if sp.is_maya():
    from solstice.pipeline.utils import mayautils
    undo_decorator = mayautils.undo
else:
    undo_decorator = decorators.empty


class OutlinerAssetItem(utils.OutlinerAssetItem, object):
    def __init__(self, asset, parent=None):
        super(OutlinerAssetItem, self).__init__(asset=asset, parent=parent)


class SolsticeBaseOutliner(utils.BaseOutliner, object):
    def __init__(self, parent=None):
        super(SolsticeBaseOutliner, self).__init__(parent=parent)

    @staticmethod
    def get_file_widget_by_category(category, parent=None):
        return None

    def init_ui(self):
        allowed_types = self.allowed_types()
        assets = sp.get_assets(allowed_types=allowed_types)
        for asset in assets:
            asset_widget = OutlinerAssetItem(asset)
            self.append_widget(asset_widget)
            self.widget_tree[asset_widget] = list()

            asset_widget.clicked.connect(self._on_item_clicked)


class SolsticeAssetsOutliner(SolsticeBaseOutliner, object):

    def __init__(self, parent=None):
        super(SolsticeAssetsOutliner, self).__init__(parent=parent)

    def allowed_types(self):
        return ['prop']

    def add_callbacks(self):
        pass


class AssetSyncer(window.Window, object):

    name = 'SolsticeShaderLibrary'
    title = 'Solstice Tools - Asset Syncer'
    version = '1.0'

    def __init__(self):
        super(AssetSyncer, self).__init__()

    def custom_ui(self):
        super(AssetSyncer, self).custom_ui()

        self.set_logo('solstice_shaderlibrary_logo')

        self.resize(400, 600)

        self.outliner = SolsticeAssetsOutliner(self)
        self.main_layout.addWidget(self.outliner)
        self.outliner.refresh_outliner()

def run():
    AssetSyncer().show()
