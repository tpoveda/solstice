#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to manage Light Rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe
from artellapipe.tools.lightrigsmanager import lightrigsmanager


class SolsticeLightRigManager(lightrigsmanager.ArtellaLightRigManager, object):
    def __init__(self, project):
        super(SolsticeLightRigManager, self).__init__(project=project)

        self.set_info_url('https://tpoveda.github.io/solstice/solsticepipeline/solsticetools/solsticelightrigmanager/')


def run():
    win = SolsticeLightRigManager(project=artellapipe.solstice)
    win.show()

    return win
