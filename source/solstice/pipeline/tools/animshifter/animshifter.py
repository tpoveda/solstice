#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to shift animation keys easily
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import sys

import maya.cmds as cmds

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

from solstice.pipeline.gui import window
from solstice.pipeline.gui import splitters
from solstice.pipeline.utils import mayautils


class SolsticeAnimShifter(window.Window, object):

    name = 'SolsticeAnimShifter'
    title = 'Solstice Tools - Solstice Animation Shifter'
    version = '1.0'

    def __init__(self):
        super(SolsticeAnimShifter, self).__init__()

        self.set_logo('solstice_animshifter_logo')

        self.resize(100, 250)

    def custom_ui(self):
        super(SolsticeAnimShifter, self).custom_ui()

        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(splitters.Splitter('Frames to Offset'))

        self.frames_spn = QSpinBox()
        self.frames_spn.setMinimum(-sys.maxint)
        self.frames_spn.setMaximum(sys.maxint)
        self.frames_spn.setValue(100)

        self.main_layout.addWidget(self.frames_spn)
        self.main_layout.addLayout(splitters.SplitterLayout())

        offset_btn = QPushButton('Offset')
        self.main_layout.addWidget(offset_btn)

        offset_btn.clicked.connect(self._on_offset)

    @mayautils.maya_undo
    def _on_offset(self):
        sel = cmds.ls(sl=True)

        if sel:
            anim_curves = cmds.listConnections(type='animCurve')
        else:
            anim_curves = cmds.ls(type=['animCurveTA',
                                        'animCurveTL',
                                        'animCurveTT',
                                        'animCurveTU'])

        for crv in anim_curves:
            cmds.keyframe(crv, edit=True, relative=True, timeChange=int(self.frames_spn.value()))


def run():
    SolsticeAnimShifter().show()
