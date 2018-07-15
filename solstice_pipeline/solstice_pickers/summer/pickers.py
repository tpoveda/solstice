#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Customized picker for Summer Character
# ==================================================================="""

import os

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_pickers.picker import picker_utils as utils
from solstice_pipeline.solstice_pickers.picker import picker_window
from solstice_pipeline.solstice_pickers.picker import picker_widget

import solstice_studiolibrarymaya
solstice_studiolibrarymaya.registerItems()
solstice_studiolibrarymaya.enableMayaClosedEvent()
import solstice_studiolibrarymaya.mayalibrarywidget
import solstice_studiolibrary.librarywidget


# --------------------------------------------------------------------------------------------
picker_images_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
picker_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
# --------------------------------------------------------------------------------------------


class SummerBodyPicker(picker_widget.Picker, object):
    def __init__(self, data_path=None, image_path=None, parent=None):
        super(SummerBodyPicker, self).__init__(data_path=data_path, image_path=image_path, parent=parent)


class SummerFacialPicker(picker_widget.Picker, object):
    def __init__(self, data_path=None, image_path=None, parent=None):
        super(SummerFacialPicker, self).__init__(data_path=data_path, image_path=image_path, parent=parent)


class SummerPicker(picker_window.PickerWindow, object):

    name = 'Summer Picker'
    title = 'Solstice Tools - Summer Picker'
    version = '1.0'
    docked = True

    def __init__(self, picker_name, picker_title, char_name, parent=None, full_window=False):

        self._full_window = full_window
        self.body_picker_data = os.path.join(picker_data_path, 'summer_body_picker_data.json')
        self.facial_picker_data = os.path.join(picker_data_path, 'summer_facial_picker_data.json')
        self.body_picker = None
        self.facial_picker = None
        self.pickers_layout = None

        super(SummerPicker, self).__init__(picker_name=picker_name, picker_title=picker_title, char_name=char_name, parent=parent)

    def get_body_picker_data(self):
        return self.body_picker_data

    def get_facial_picker_data(self):
        return self.facial_picker_data

    def get_body_picker(self):
        return SummerBodyPicker(data_path=self.get_body_picker_data(), image_path=os.path.join(picker_images_path, 'summer_body.svg'))

    def get_facial_picker(self):
        return SummerFacialPicker(data_path=self.get_body_picker_data(), image_path=os.path.join(picker_images_path, 'summer_body.svg'))

    def load_pickers(self, full_window=False):
        super(SummerPicker, self).load_pickers(full_window=full_window)

        if self.body_picker:
            self.body_picker.setParent(None)
            self.body_picker.deleteLater()
        if self.facial_picker:
            self.facial_picker.setParent(None)
            self.facial_picker.deleteLater()
        if self.pickers_layout:
            self.pickers_layout.setParent(None)
            self.pickers_layout.deleteLater()

        self.pickers_layout = QHBoxLayout()
        self.pickers_layout.setContentsMargins(5, 5, 5, 5)
        self.pickers_layout.setSpacing(2)
        self.main_layout.addLayout(self.pickers_layout)

        self.body_picker = self.get_body_picker()
        self.facial_picker = self.get_facial_picker()
        self.pose_widget = solstice_studiolibrary.librarywidget.LibraryWidget.instance()
        solstice_project_folder = os.environ.get('SOLSTICE_PROJECT')
        if not os.path.exists(solstice_project_folder):
            sp.update_solstice_project()
            solstice_project_folder = os.environ.get('SOLSTICE_PROJECT')
        if solstice_project_folder and os.path.exists(solstice_project_folder):
            solstice_assets = os.path.join(solstice_project_folder, 'Asset')
            if os.path.exists(solstice_assets):
                anims = os.path.join(solstice_assets, 'AnimationLibrary')
                if os.path.exists(anims):
                    self.pose_widget.setPath(anims)
                else:
                    self.pose_widget.setPath(solstice_assets)
            else:
                self.pose_widget.setPath(solstice_project_folder)

        if full_window:
            for picker in [self.body_picker, self.facial_picker]:
                self.pickers_layout.addWiget(picker)
        else:
            self.char_tab = QTabWidget()
            self.pickers_layout.addWidget(self.char_tab)
            self.char_tab.addTab(self.body_picker, 'Body')
            self.char_tab.addTab(self.facial_picker, 'Facial')
            self.char_tab.addTab(self.pose_widget, 'Pose Library')

    def get_full_window(self):
        return self._full_window

    def set_full_window(self, full_window):
        self._full_window = full_window

    full_window = property(get_full_window, set_full_window)

    def custom_ui(self):
        super(SummerPicker, self).custom_ui()

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.load_pickers(full_window=self._full_window)
        self.update_pickers()

    def update_pickers(self):
        """
        Update the state of the character pickers
        """

        for picker in [self.body_picker, self.facial_picker]:
            picker.namespace = self.namespace.currentText()

    def reload_data(self):
        """
        Relaod data used by pickers and recreate all the picker buttons and properties
        TODO: Very slow function, avoid to use it
        """

        for picker in [self.body_picker, self.facial_picker]:
            picker.reload_data()
        self.body_picker.reload_data()


def run(full_window=True):
    utils.dock_window(picker_name='summer_picker', picker_title='Solstice - Summer Picker', character_name='Summer', dialog_class=SummerPicker)