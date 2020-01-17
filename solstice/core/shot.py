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
from artellapipe.core import shot

from artellapipe.libs.kitsu.core import kitsulib

LOGGER = logging.getLogger()


class SolsticeShot(shot.ArtellaShot, object):
    def __init__(self, project, shot_data):

        self._name_dict = dict()

        super(SolsticeShot, self).__init__(project=project, shot_data=shot_data)

    def get_sequence(self):
        """
        Override base shot.ArtellaShot get_sequence_function
        Returns the name of the sequence this shot belongs to
        :return: str
        """

        sequence_attr = artellapipe.ShotsMgr().config.get('data', 'sequence_attribute')
        sequence_id = self._shot_data.get(sequence_attr, None)
        if not sequence_id:
            LOGGER.warning(
                'Impossible to retrieve sequence name because shot data does not contains "{}" attribute.'
                '\nSequence Data: {}'.format(sequence_attr, self._shot_data))
            return None

        if self._name_dict and sequence_id in self._name_dict:
            return self._name_dict[sequence_id]

        sequence_name = kitsulib.get_shot_sequence({'parent_id': sequence_id}).name
        self._name_dict = {sequence_id: sequence_name}

        return sequence_name


artellapipe.register.register_class('Shot', SolsticeShot)
