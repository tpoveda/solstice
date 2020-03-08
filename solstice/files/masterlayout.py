#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for masater layout sequence files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

import tpDcc as tp

from artellapipe.core import sequencefile


class SolsticeMasterLayoutSequenceFile(sequencefile.ArtellaSequenceFile, object):
    def __init__(self, sequence=None):
        super(SolsticeMasterLayoutSequenceFile, self).__init__(file_sequence=sequence)

    def _open_file(self, file_path):
        if not file_path:
            return False

        if os.path.isfile(file_path) and tp.Dcc.scene_name() != file_path:
            tp.Dcc.open_file(file_path)

        return True
