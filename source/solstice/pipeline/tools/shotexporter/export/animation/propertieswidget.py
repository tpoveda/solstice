#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains definition for animation property list widget
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import solstice.pipeline as sp
from solstice.pipeline.tools.shotexporter.core import defines
from solstice.pipeline.tools.shotexporter.widgets import propertieslist


class AnimationPropertiesWidget(propertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(AnimationPropertiesWidget, self).__init__(parent=parent)

    def update_attributes(self, asset_widget):
        if asset_widget == self._current_asset:
            return

        self.clear_properties()
        self._current_asset = asset_widget

        xform_attrs = sp.dcc.list_attributes(asset_widget.asset.name)
        for attr in xform_attrs:
            if attr not in defines.MUST_ATTRS:
                continue
            new_attr = self.add_attribute(attr)
            if self._current_asset.attrs[new_attr.name] is True:
                new_attr.check()
            else:
                new_attr.uncheck()

        abc_attrs = sp.dcc.list_attributes(asset_widget.abc_node)
        for attr in abc_attrs:
            if attr not in defines.ABC_ATTRS:
                continue
            new_attr = self.add_attribute(attr)
            if self._current_asset.abc_attrs[new_attr.name] is True:
                new_attr.check()
            else:
                new_attr.uncheck()

    def _on_update_attribute(self, attr_name, flag):
        if not self._current_asset:
            return

        if attr_name in self._current_asset.attrs.keys():
            self._current_asset.attrs[attr_name] = flag
            return
        elif attr_name in self._current_asset.abc_attrs.keys():
            self._current_asset.abc_attrs[attr_name] = flag
            return

        sp.logger.warning('Impossible to udpate attribute {} because node {} has no that attribute!'.format(attr_name, self._current_asset.asset))
