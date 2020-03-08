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
from artellapipe.libs.naming.core import naminglib

LOGGER = logging.getLogger()


class SolsticeShot(shot.ArtellaShot, object):
    def __init__(self, project, shot_data):

        self._name_dict = dict()

        super(SolsticeShot, self).__init__(project=project, shot_data=shot_data)

    def get_path(self):
        """
        Implements base shot.ArtellaShot get_path function
        :return: str
        """

        shot_file_class = artellapipe.FilesMgr().get_file_class('rough')
        if not shot_file_class:
            LOGGER.warning('Impossible to retrieve Shot File for "{}"'.format(self.get_name()))
            return None

        file_type = self.get_file_type('rough')
        print(file_type)

    def get_number(self):
        """
        Override base shot.ArtellaShot get_sequence function
        Returns the number of the shot
        :return: str
        """

        shot_rule_name = artellapipe.ShotsMgr().config.get('data', 'shot_rule')
        rule = naminglib.ArtellaNameLib().get_rule(shot_rule_name)
        if not rule:
            LOGGER.warning('No Rule found with name: "{}"'.format(shot_rule_name))

        current_rule = None
        try:
            current_rule = naminglib.ArtellaNameLib().active_rule()
            naminglib.ArtellaNameLib().set_active_rule(shot_rule_name)
            parsed_rule = naminglib.ArtellaNameLib().parse(self.get_name())
        finally:
            if current_rule:
                naminglib.ArtellaNameLib().set_active_rule(current_rule)

        if not parsed_rule:
            LOGGER.warning('Impossible to retrieve rule number from shot name: {}'.format(self.get_name()))
            return None

        return parsed_rule.get('shot_number', None)

    def get_sequence(self):
        """
        Override base shot.ArtellaShot get_sequence function
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
