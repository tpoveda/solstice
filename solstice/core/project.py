#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Solstice Artella project
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from artellapipe.core import project as artella_project


class Solstice(artella_project.ArtellaProject, object):

    def __init__(self):
        super(Solstice, self).__init__(name='Solstice')
