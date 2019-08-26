#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for lighting files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import artellapipe

from artellapipe.tools.shotmanager.core import exporter, shotexporter
from artellapipe.tools.shotmanager.widgets import exportlist, exportpropertieslist

import solstice
from solstice.core import defines as solstice_defines


class LightingExportList(exportlist.BaseExportList, object):

    def __init__(self, project, parent=None):
        super(LightingExportList, self).__init__(project=project, parent=parent)


class LightingPropertiesWidget(exportpropertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(LightingPropertiesWidget, self).__init__(
            name='LightingPropertiesEditor',
            label='Lighting Properties',
            title='Lighting Properties Editor',
            parent=parent
        )


class LightingExporter(exporter.BaseExporter, object):

    EXPORTER_NAME = 'Lighting'
    EXPORTER_ICON = solstice.resource.icon('lighting')
    EXPORTER_FILE = solstice_defines.SOLSTICE_ANIMATION_SHOT_FILE_TYPE
    EXPORTER_EXTENSION = solstice_defines.SOLSTICE_ANIMATION_EXTENSION
    EXPORT_BUTTON_TEXT = 'SAVE LIGHTING'
    EXPORTER_LIST_WIDGET_CLASS = LightingExportList
    EXPORTER_PROPERTIES_WIDGET_CLASS = LightingPropertiesWidget

    def __init__(self, project, parent=None):
        super(LightingExporter, self).__init__(project=project, parent=parent)


shotexporter.register_exporter(LightingExporter)
