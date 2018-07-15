#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Picker View Class
# ==================================================================="""

import os

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

from solstice_pipeline.solstice_pickers.picker import picker_window
from solstice_pipeline.solstice_pickers.picker import picker_utils as utils


class PickerScene(QGraphicsScene, object):
    """
    Picker scene
    """

    __DEFAULT_SCENE_WIDTH__ = 100
    __DEFAULT_SCENE_HEIGHT__ = 200

    def __init__(self, data_path=None, namespace='', parent=None):
        super(PickerScene, self).__init__(parent=parent)

        self._data_path = data_path
        self._buttons = list()
        self._data_buttons = None
        self._parts = list()
        self._namespace = namespace

        self.set_default_size()

    def get_namespace(self):
        return self._namespace

    def set_namespace(self, namespace):
        self._namespace = namespace

    def get_parts(self):
        return self._parts

    namespace = property(get_namespace, set_namespace)
    parts = property(get_parts)

    def get_bounding_rect(self):
        """
        Returns the bounding rect of the scene taking in account all the items inside of it
        :return: QRect
        """

        return self.itemsBoundingRect()

    def set_size(self, width, height):
        """
        Set the size of the scene
        :param width: int, width of the scene
        :param height: int, height of the scene
        """

        self.setSceneRect(-width*0.5, -height*0.5, width, height)

    def set_default_size(self):
        """
        Sets the scene with default size
        """

        self.set_size(self.__DEFAULT_SCENE_WIDTH__, self.__DEFAULT_SCENE_HEIGHT__)

    def reload_data(self):
        """
        Reloads the data of the picker
        """

        self.clear()

        if self._data_path is not '' and self._data_path is not None:
            if os.path.isfile(self._data_path):
                self.load_data(self._dat_path)

    def update_state(self):
        """
        Updates the state of the picker
        Useful when the picker is not correctly sync with the state of the character
        This can happen when using undo/redo actions
        :return:
        """

        # TODO: Use Maya callbacks to call this method each time a undo/redo action is done

        for part in self._parts:
            if part.has_fkik():
                if part.get_fkik(as_text=True) == 'FK':
                    part.set_fk()
                else:
                    part.set_ik()

    def add_button(self, new_button=None):
        """
        Adds a new picker button to the scene
        :param new_button: SolsticeButton
        """

        if new_button is None:
            pass

