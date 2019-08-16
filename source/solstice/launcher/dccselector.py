#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains DCC Selector implementation for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import solstice
from artellalauncher.core import dccselector


class SolsticeDCCSelector(dccselector.DCCSelector, object):
    def __init__(self, launcher, parent=None):
        super(SolsticeDCCSelector, self).__init__(launcher=launcher, parent=parent)

    def ui(self):
        super(SolsticeDCCSelector, self).ui()

        selector_logo = solstice.resource.pixmap(name='launcher_logo', extension='png')
        self.add_logo(selector_logo, 930, 0)

    def _get_title_pixmap(self):
        return solstice.resource.pixmap(name='title_background', extension='png')
