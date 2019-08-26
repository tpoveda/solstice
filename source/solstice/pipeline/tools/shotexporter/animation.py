#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exporter widget for animation files
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


class AnimationExportList(exportlist.BaseExportList, object):

    def __init__(self, project, parent=None):
        super(AnimationExportList, self).__init__(project=project, parent=parent)


class AnimationPropertiesWidget(exportpropertieslist.BasePropertiesListWidget, object):
    def __init__(self, parent=None):
        super(AnimationPropertiesWidget, self).__init__(
            name='AnimationPropertiesEditor',
            label='Animation Properties',
            title='Animation Properties Editor',
            parent=parent
        )


class AnimationExporter(exporter.BaseExporter, object):

    EXPORTER_NAME = 'Animation'
    EXPORTER_ICON = solstice.resource.icon('animation')
    EXPORTER_FILE = solstice_defines.SOLSTICE_ANIMATION_SHOT_FILE_TYPE
    EXPORTER_EXTENSION = solstice_defines.SOLSTICE_ANIMATION_EXTENSION
    EXPORT_BUTTON_TEXT = 'SAVE ANIMATION'
    EXPORTER_LIST_WIDGET_CLASS = AnimationExportList
    EXPORTER_PROPERTIES_WIDGET_CLASS = AnimationPropertiesWidget

    def __init__(self, project, parent=None):
        super(AnimationExporter, self).__init__(project=project, parent=parent)


shotexporter.register_exporter(AnimationExporter)
