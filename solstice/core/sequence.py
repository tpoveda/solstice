#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class that defines Artella Shot for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import artellapipe.register
from artellapipe.core import sequence

LOGGER = logging.getLogger()


class SolsticeSequence(sequence.ArtellaSequence, object):
    def __init__(self, project, sequence_data):

        self._name_dict = dict()

        super(SolsticeSequence, self).__init__(project=project, sequence_data=sequence_data)


artellapipe.register.register_class('Sequence', SolsticeSequence)
