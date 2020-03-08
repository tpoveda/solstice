#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for high/proxy editor
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging.config
from functools import partial

from Qt.QtWidgets import *

import tpDcc as tp

from tpDcc.libs.qt.widgets import label

import artellapipe
from artellapipe.tools.tagger.widgets import taggereditor

LOGGER = logging.getLogger()


class HighProxyEditor(taggereditor.TaggerEditor, object):

    EDITOR_TYPE = 'Proxy/High'

    def __init__(self, project, parent=None):
        super(HighProxyEditor, self).__init__(project=project, parent=parent)

    def ui(self):
        super(HighProxyEditor, self).ui()

        low_layout = QHBoxLayout()
        low_lbl = QLabel('Proxy: ')
        self._low_line = label.DragDropLine()
        self._low_line.setReadOnly(True)
        low_layout.addWidget(low_lbl)
        low_layout.addWidget(self._low_line)
        self.main_layout.addLayout(low_layout)
        high_layout = QHBoxLayout()
        high_lbl = QLabel('High: ')
        self._high_line = label.DragDropLine()
        self._high_line.setReadOnly(True)
        high_layout.addWidget(high_lbl)
        high_layout.addWidget(self._high_line)
        self.main_layout.addLayout(high_layout)

        self._check_btn = QPushButton('Update Proxy/Hires groups')
        self.main_layout.addWidget(self._check_btn)

    def setup_signals(self):
        self._check_btn.clicked.connect(partial(self.update_data, None))

        # self.low_line.textChanged.connect(partial(self.update_data, None))
        # self.high_line.textChanged.connect(partial(self.update_data, None))

    def initialize(self):
        """
        Initializes tagger editor
        """

        pass

    def reset(self):
        """
        Function that resets all editor information
        """

        try:
            self._high_line.blockSignals(True)
            self._low_line.blockSignals(True)
            self._high_line.setText('')
            self._low_line.setText('')
        finally:
            self._high_line.blockSignals(False)
            self._low_line.blockSignals(False)

    def update_tag_buttons_state(self, sel=None):
        """
        Updates the state of the tag buttons in the editor
        :param sel: variant
        """

        tag_data_node = artellapipe.TagsMgr().get_tag_data_node_from_current_selection(sel)
        if tag_data_node is None or not tp.Dcc.object_exists(tag_data_node):
            return

        attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='proxy')
        if attr_exists:
            proxy_group = tp.Dcc.list_connections(node=tag_data_node, attribute_name='proxy')
            if proxy_group:
                proxy_group = proxy_group[0]
            if proxy_group is not None and tp.Dcc.object_exists(proxy_group):
                self._low_line.setText(proxy_group)

        attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='hires')
        if attr_exists:
            hires_group = tp.Dcc.list_connections(node=tag_data_node, attribute_name='hires')
            if hires_group:
                hires_group = hires_group[0]
            if hires_group is not None and tp.Dcc.object_exists(hires_group):
                self._high_line.setText(hires_group)

    def fill_tag_node(self, tag_data_node, *args, **kwargs):
        """
        Fills given tag node with the data managed by this editor
        :param tag_data_node: str
        """

        sel = kwargs.pop('sel', None)

        self.update_proxy_group()
        self.update_hires_group()
        self.update_tag_buttons_state(sel)

    @staticmethod
    def update_proxy_group(tag_data=None):
        """
        Updates the current proxy group
        :param tag_data: str
        :return:
        """

        current_selection = artellapipe.TagsMgr().get_current_selection()

        if not tag_data:
            tag_data_node = artellapipe.TagsMgr().get_tag_data_node_from_current_selection()
            if tag_data_node is None or not tp.Dcc.object_exists(tag_data_node):
                return
        else:
            if not tp.Dcc.object_exists(tag_data):
                LOGGER.error('Tag Data {} does not exists in current scene!'.format(tag_data))
                return False
            tag_data_node = tag_data

        attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='proxy')
        if not attr_exists:
            tp.Dcc.add_message_attribute(node=tag_data_node, attribute_name='proxy')

        sel_name = tp.Dcc.node_long_name(current_selection)

        # Check proxy group connection
        proxy_path = None
        if tp.Dcc.object_exists(sel_name):
            name = sel_name.split('|')[-1]
            proxy_name = '{}_proxy_grp'.format(name)
            children = tp.Dcc.list_relatives(
                node=sel_name, all_hierarchy=True, full_path=True, relative_type='transform')
            if not children:
                LOGGER.error('Proxy Group not found!')
                return False
            for obj in children:
                base_name = obj.split('|')[-1]
                if base_name == proxy_name:
                    if proxy_path is None:
                        proxy_path = obj
                    else:
                        LOGGER.error(
                            'Multiple proxy groups in the asset. Asset only can have one proxy group: {}'.format(
                                proxy_name))
                        return False
        if proxy_path is None or not tp.Dcc.object_exists(proxy_path):
            LOGGER.error('Proxy Group not found!')
            return False
        try:
            tp.Dcc.lock_attribute(node=tag_data_node, attribute_name='proxy')
            tp.Dcc.connect_attribute(proxy_path, 'message', tag_data, 'proxy', force=True)
        except Exception:
            pass

        tp.Dcc.lock_attribute(node=tag_data_node, attribute_name='proxy')

        return True

    @staticmethod
    def update_hires_group(tag_data=None):
        """
        Updates the current hires group
        :param tag_data: str
        :return:
        """

        current_selection = artellapipe.TagsMgr().get_current_selection()

        if not tag_data:
            tag_data_node = artellapipe.TagsMgr().get_tag_data_node_from_current_selection()
            if tag_data_node is None or not tp.Dcc.object_exists(tag_data_node):
                return
        else:
            if not tp.Dcc.object_exists(tag_data):
                LOGGER.error('Tag Data {} does not exists in current scene!'.format(tag_data))
                return False
            tag_data_node = tag_data

        attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='hires')
        if not attr_exists:
            tp.Dcc.add_message_attribute(node=tag_data_node, attribute_name='hires')

        sel_name = tp.Dcc.node_long_name(node=current_selection)

        # Check hires group connection
        hires_path = None
        if tp.Dcc.object_exists(sel_name):
            name = sel_name.split('|')[-1]
            hires_name = '{}_hires_grp'.format(name)
            children = tp.Dcc.list_relatives(
                node=sel_name, all_hierarchy=True, full_path=True, relative_type='transform')
            if not children:
                LOGGER.error('Hires Group not found!')
                return False
            for obj in children:
                base_name = obj.split('|')[-1]
                if base_name == hires_name:
                    if hires_path is None:
                        hires_path = obj
                    else:
                        LOGGER.error(
                            'Multiple hires groups in the asset. Asset only can have one hires group: {}'.format(
                                hires_name))
                        return False
        if hires_path is None or not tp.Dcc.object_exists(hires_path):
            LOGGER.error('Hires Group not found!')
            return False
        try:
            tp.Dcc.unlock_attribute(node=tag_data_node, attribute_name='hires')
            tp.Dcc.connect_attribute(hires_path, 'message', tag_data_node, 'hires', force=True)
        except Exception:
            pass

        tp.Dcc.lock_attribute(tag_data_node, 'hires')

        return True
