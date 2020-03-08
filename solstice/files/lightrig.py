#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for light rig files in Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

import tpDcc as tp

from artellapipe.core import file

LOGGER = logging.getLogger()


class SolsticeLightRigFile(file.ArtellaFile, object):
    def __init__(self, project, file_name, file_path=None, file_extension=None):
        self._original_name = file_name.replace('_', ' ')
        super(SolsticeLightRigFile, self).__init__(
            project=project, file_name=file_name, file_path=file_path, file_extension=file_extension)

    def get_template_dict(self, **kwargs):
        """
        Implements get_template_dict() function
        :return: dict
        """

        return {
            'project_id': self._project.id,
            'project_id_number': self._project.id_number,
            'light_rig_name': self._original_name
        }

    def _reference_file(self, file_path, *args, **kwargs):
        LOGGER.info('Referencing: {}'.format(file_path))
        tp.Dcc.reference_file(file_path)
