#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to detect errors and trace calls for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"


import artellapipe
from artellapipe.tools.bugtracker import bugtracker


class SolsticeBugTracker(bugtracker.ArtellaBugTracker, object):
    def __init__(self, project, tool_name=None, parent=None):
        super(SolsticeBugTracker, self).__init__(project=project, tool_name=tool_name, parent=parent)

    def ui(self):
        super(SolsticeBugTracker, self).ui()

        logo_pixmap = artellapipe.solstice.resource.pixmap(name='bugtracker_logo', extension='png')
        self.set_logo(logo_pixmap)
