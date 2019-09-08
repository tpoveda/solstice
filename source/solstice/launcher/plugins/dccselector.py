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

import os

import solstice
from artellalauncher.core import dccselector


class SolsticeDCCSelector(dccselector.DCCSelector, object):
    def __init__(self, project, parent=None):
        super(SolsticeDCCSelector, self).__init__(project=project, parent=parent)

    def init_config(self):
        mod_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
        mod_folder = os.path.dirname(os.path.abspath(__file__))
        plugin_config = os.path.join(mod_folder, mod_name+'.json')
        if os.path.isfile(plugin_config):
            self.load_dccs(plugin_config)

    # def ui(self):
    #     super(SolsticeDCCSelector, self).ui()

    #     selector_logo = solstice.resource.pixmap(name='launcher_logo', extension='png')
    #     self.add_logo(selector_logo, 930, 0)
    #
    #     self.set_info_url('https://tpoveda.github.io/solstice/pipeline/launcher/usage/')
    #
    # def _get_title_pixmap(self):
    #     return solstice.resource.pixmap(name='title_background', extension='png')
