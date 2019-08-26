#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains transform override implementation for Solstice Shot Assembler
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtWidgets import *

import tpDccLib as tp

import artellapipe
from artellapipe.tools.shotmanager.core import override, shotassembler

import solstice
from solstice.core import defines


class SolsticeTransformOverride(override.ArtellaBaseOverride, object):

    OVERRIDE_NAME = 'Transform'
    OVERRIDE_ICON = solstice.resource.icon('coordinate')
    OVERRIDE_EXTENSION = defines.SOLSTICE_TRANSFORM_OVERRIDE_EXTENSION

    def __init__(self, project, asset_node, data=None, file_path=None):
        super(SolsticeTransformOverride, self).__init__(project=project, asset_node=asset_node, data=data, file_path=file_path)

    @classmethod
    def create_from_data(cls, project, data, file_path=None):
        """
        Implements base ArtellaBaseOverride create_from_data function
        Creates a new instance of the override by a given data
        :param data: dict
        :param file_path: str
        :return: SolsticeTransformOverride
        """

        asset_node = data.keys()[0]
        override_data = data[asset_node]
        asset_node = project.ASSET_NODE_CLASS(project=project, node=asset_node)

        return cls(project=project, asset_node=asset_node, data=override_data, file_path=file_path)

    def apply(self, *args, **kwargs):
        """
        Implements base ArtellaBaseOverride apply function
        Applies current override
        :param args: list
        :param kwargs: dict
        """

        if not tp.Dcc.object_exists(self._asset_node.node):
            artellapipe.logger.warning('Impossible to apply Transform Shot Override to inexting node: {}'.format(self._asset_node.node))
            return

        data = self.get_data()
        if not data:
            artellapipe.logger.warning('Transform Override has no data to apply to node: {}'.format(self._asset_node.node))
            return

        for attr_name, attr_value in data.items():
            if not tp.Dcc.attribute_exists(node=self._asset_node.node, attribute_name=attr_name):
                artellapipe.logger.warning('Attribute with name: {} not found in node: {}!'.format(attr_name, self._asset_node.node))
                continue

            tp.Dcc.set_attribute_value(node=self._asset_node.node, attribute_name=attr_name, attribute_value=attr_value)

    def default_value(self):
        """
        Overrides base ArtellaBaseOverride default_value function
        Returns the default value stored by the override
        :return: dict
        """

        return {
            'translate': True,
            'rotate': True,
            'scale': True
        }

    def get_editor_widget(self):
        """
        Overrides base ArtellaBaseOverride get_editor_widget function
        Returns custom widget used by Override Editor to edit override attributes
        :return: QWidget
        """

        return SolsticeTransformEditorWidget(self)

    def _get_data_to_save(self):
        """
        Overrides base ArtellaOverrideWidget get_data function
        Returns data that should be stored
        :return: dict
        """

        data_to_save = dict()

        current_data = self.get_data()

        attrs_to_save = list()
        if current_data.get('translate', False):
            attrs_to_save.append('translate')
        if current_data.get('rotate', False):
            attrs_to_save.append('rotate')
        if current_data.get('scale', False):
            attrs_to_save.append('scale')

        if not attrs_to_save:
            return data_to_save

        data_to_save[self._asset_node.node] = dict()

        for axis in 'XYZ':
            for attr in attrs_to_save:
                attr_to_save = '{}{}'.format(attr, axis)
                if not tp.Dcc.attribute_exists(node=self._asset_node.node, attribute_name=attr_to_save):
                    artellapipe.logger.warning('{} >> Impossible to store attribute {} for node {}! Skipping ...'.format(self.OVERRIDE_NAME, attr_to_save, self._asset_node.node))
                    continue
                data_to_save[self._asset_node.node][attr_to_save] = tp.Dcc.get_attribute_value(node=self._asset_node.node, attribute_name=attr_to_save)

        return data_to_save


class SolsticeTransformEditorWidget(override.ArtellaOverrideWidget, object):
    def __init__(self, override, parent=None):
        super(SolsticeTransformEditorWidget, self).__init__(override=override, parent=parent)

    def ui(self):
        super(SolsticeTransformEditorWidget, self).ui()

        override_data = self._override.get_data()

        self._translate_override_cbx = QCheckBox('Translate')
        self._rotate_override_cbx = QCheckBox('Rotate')
        self._scale_override_cbx = QCheckBox('Scale')

        self._translate_override_cbx.setChecked(override_data.get('translate', False))
        self._rotate_override_cbx.setChecked(override_data.get('rotate', False))
        self._scale_override_cbx.setChecked(override_data.get('scale', False))

        self.main_layout.addWidget(self._translate_override_cbx)
        self.main_layout.addWidget(self._rotate_override_cbx)
        self.main_layout.addWidget(self._scale_override_cbx)

    def get_data(self):
        """
        Overrides base ArtellaOverrideWidget get_data function
        Returns data that should be stored in override
        :return: dict
        """

        return {
            'translate': self._translate_override_cbx.isChecked(),
            'rotate': self._rotate_override_cbx.isChecked(),
            'scale': self._scale_override_cbx.isChecked()
        }


shotassembler.register_override(SolsticeTransformOverride)
