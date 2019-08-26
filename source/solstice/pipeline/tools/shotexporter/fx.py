#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for FX files
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


class FXExportList(exportlist.BaseExportList, object):

    def __init__(self, project, parent=None):
        super(FXExportList, self).__init__(project=project, parent=parent)


class FXPropertiesWidget(exportpropertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(FXPropertiesWidget, self).__init__(
            name='FXPropertiesEditor',
            label='FX Properties',
            title='FX Properties Editor',
            parent=parent
        )


class FXExporter(exporter.BaseExporter, object):

    EXPORTER_NAME = 'FX'
    EXPORTER_ICON = solstice.resource.icon('fx')
    EXPORTER_FILE = solstice_defines.SOLSTICE_FX_SHOT_FILE_TYPE
    EXPORTER_EXTENSION = solstice_defines.SOLSTICE_FX_EXTENSION
    EXPORT_BUTTON_TEXT = 'SAVE FX'
    EXPORTER_LIST_WIDGET_CLASS = FXExportList
    EXPORTER_PROPERTIES_WIDGET_CLASS = FXPropertiesWidget

    def __init__(self, project, parent=None):
        super(FXExporter, self).__init__(project=project, parent=parent)


shotexporter.register_exporter(FXExporter)
