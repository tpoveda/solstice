#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Shelf
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDccLib

from artellapipe.utils import resource


class SolsticeShelf(tpDccLib.Shelf, object):

    ICONS_PATHS = resource.ResourceManager().get_resources_paths()

    def __init__(self,
                 name='SolsticeShelf',
                 label_background=(0, 0, 0, 0),
                 label_color=(0.9, 0.9, 0.9),
                 category_icon=None):

        enable_labels = False
        if tpDccLib.is_houdini():
            enable_labels = True

        super(SolsticeShelf, self).__init__(
            name=name,
            label_background=label_background,
            label_color=label_color,
            category_icon=category_icon,
            enable_labels=enable_labels)
