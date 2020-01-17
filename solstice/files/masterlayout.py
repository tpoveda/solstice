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

from artellapipe.core import sequencefile


class SolsticeMasterLayoutSequenceFile(sequencefile.ArtellaSequenceFile, object):
    def __init__(self, sequence=None):
        super(SolsticeMasterLayoutSequenceFile, self).__init__(file_sequence=sequence)
