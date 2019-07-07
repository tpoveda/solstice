#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget definition for model panels
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.utils import qtutils

if sp.is_maya():
    import maya.cmds as cmds
    import maya.OpenMayaUI as OpenMayaUI


class ModelPanelWidget(QWidget, object):
    def __init__(self, parent, name='capturedModelPanel', **kwargs):
        super(ModelPanelWidget, self).__init__(parent, **kwargs)

        unique_name = name + str(id(self))
        self.setObjectName(unique_name+'Widget')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0 ,0)
        main_layout.setObjectName(unique_name+'Layout')
        self.setLayout(main_layout)

        self._model_panel = None

        if sp.is_maya():
            cmds.setParent(main_layout.objectName())
            self._model_panel = cmds.modelPanel(unique_name, label='ModelPanel')

        self.set_model_panel_options()

    def set_model_panel_options(self):
        model_panel = self.name()

        if sp.is_maya():
            cmds.modelEditor(model_panel, edit=True, allObjects=False)
            cmds.modelEditor(model_panel, edit=True, grid=False)
            cmds.modelEditor(model_panel, edit=True, dynamics=False)
            cmds.modelEditor(model_panel, edit=True, activeOnly=False)
            cmds.modelEditor(model_panel, edit=True, manipulators=False)
            cmds.modelEditor(model_panel, edit=True, headsUpDisplay=False)
            cmds.modelEditor(model_panel, edit=True, selectionHiliteDisplay=False)
            cmds.modelEditor(model_panel, edit=True, polymeshes=True)
            cmds.modelEditor(model_panel, edit=True, nurbsSurfaces=True)
            cmds.modelEditor(model_panel, edit=True, subdivSurfaces=True)
            cmds.modelEditor(model_panel, edit=True, displayTextures=True)
            cmds.modelEditor(model_panel, edit=True, displayAppearance="smoothShaded")

        current_model_panel = sys.solstice.dcc.get_current_model_panel()
        if current_model_panel:
            if sp.is_maya():
                camera = cmds.modelEditor(current_model_panel, query=True, camera=True)
                display_lights = cmds.modelEditor(current_model_panel, query=True, displayLights=True)
                display_textures = cmds.modelEditor(current_model_panel, query=True, displayTextures=True)
                cmds.modelEditor(model_panel, edit=True, camera=camera)
                cmds.modelEditor(model_panel, edit=True, displayLights=display_lights)
                cmds.modelEditor(model_panel, edit=True, displayTextures=display_textures)

    def name(self):
        """
        Returns the name of the model panel
        :return: str
        """

        return self._model_panel

    def model_panel(self):
        """
        Returns model panel isntance
        :return: QWidget
        """
        if sp.is_maya():
            ptr = OpenMayaUI.MQtUtil.findControl(self._model_panel)
            return qtutils.wrapinstance(ptr, QWidget)

    def bar_layout(self):
        if sp.is_maya():
            name = cmds.modelPanel(self._model_panel, query=True, barLayout=True)
            ptr = OpenMayaUI.MQtUtil.findControl(name)
            return qtutils.wrapinstance(ptr, QObject)

    def hide_bar_layout(self):
        self.bar_layout().hide()

    def hide_menu_bar(self):
        cmds.modelPanel(self._model_panel, edit=True, menuBarVisible=False)

    def set_camera(self, name):
        cmds.modelPanel(self._model_panel, edit=True, cam=name)