#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_animtools.py
# by Tomas Poveda
# Tool that contains utility tools related with generic animation
# ______________________________________________________________________
# ==================================================================="""

import sys

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *

import maya.cmds as cmds

from solstice_pipeline.solstice_gui import solstice_windows, solstice_accordion
from solstice_pipeline.resources import solstice_resource


class KeyframeTools(QWidget, object):
    def __init__(self, parent=None):
        super(KeyframeTools, self).__init__(parent=parent)

        offset_layout = QHBoxLayout()
        offset_layout.setContentsMargins(2, 2, 2, 2)
        offset_layout.setSpacing(2)
        offset_frames_lbl = QLabel('Offset Frames: ')
        self.frame_offset_spn = QSpinBox()
        self.frame_offset_spn.setMinimum(-sys.maxint)
        self.frame_offset_spn.setMaximum(sys.maxint)
        self.frame_offset_spn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vertical_separator = QFrame()
        vertical_separator.setFrameShape(QFrame.VLine)
        vertical_separator.setFrameShadow(QFrame.Sunken)
        go_icon = solstice_resource.icon('go')
        apply_anim_offset_btn = QPushButton()
        apply_anim_offset_btn.setIcon(go_icon)
        apply_anim_offset_btn.setMaximumWidth(30)
        apply_anim_offset_btn.setIconSize(QSize(22, 22))

        offset_layout.addWidget(offset_frames_lbl)
        offset_layout.addWidget(self.frame_offset_spn)
        offset_layout.addWidget(vertical_separator)
        offset_layout.addWidget(apply_anim_offset_btn)

        self.setLayout(offset_layout)

        apply_anim_offset_btn.clicked.connect(self._on_set_offset_animation)

    @staticmethod
    def offset_animation(offset):
        """
        Offset keys applied to the anim curves of the selected objects
        :param offset: float, offset to apply to the keyframes
        """

        anim_curves = cmds.ls(type=['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU'])
        for crv in anim_curves:
            cmds.keyframe(crv, edit=True, relative=True, timeChange=offset)

    def _on_set_offset_animation(self):
        offset = self.frame_offset_spn.value()
        self.offset_animation(offset)


class AnimTools(solstice_windows.Window, object):
    name = 'Solstice_AnimTools'
    title = 'Solstice Tools - Animation Tools'
    version = '1.0'

    def __init__(self, name='AnimToolsWindow', parent=None):
        super(AnimTools, self).__init__()

    def custom_ui(self):
        super(AnimTools, self).custom_ui()

        self.set_logo('solstice_animtools_logo')

        self.main_widget = solstice_accordion.AccordionWidget(parent=self)
        self.main_widget.rollout_style = solstice_accordion.AccordionStyle.ROUNDED
        self.main_layout.addWidget(self.main_widget)

        keyframe_widget = KeyframeTools()
        self.main_widget.add_item('Keyframes', keyframe_widget, collapsed=False)


def run():
    win = AnimTools.show()
