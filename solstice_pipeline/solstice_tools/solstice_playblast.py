#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Tool to capture Playblast for Solstice Short Film
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

from solstice_gui import solstice_windows, solstice_accordion


class PlayblastPreview(QWidget, object):
    """
    Playtblas image preview
    """

    __DEFAULT_WIDTH__ = 320
    __DEFAULT_HEIGHT__ = 180

    def __init__(self, options, validator, parent=None):
        super(PlayblastPreview, self).__init__(parent=parent)


class SolsticePlayBlast(solstice_windows.Window, object):

    name = 'Solstice_PlayBlast'
    title = 'Solstice Tools - Playblast Tool'
    version = '1.0'
    docked = True

    def __init__(self, parent=None, **kwargs):
        super(SolsticePlayBlast, self).__init__(parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticePlayBlast, self).custom_ui()

        self.set_logo('solstice_playblast_logo')

        self.main_widget = solstice_accordion.AccordionWidget(parent=self)
        self.main_widget.rollout_style = solstice_accordion.AccordionStyle.MAYA

        # self.main_widget.add_item('Preview', PlayblastPreview(parent=self), collapsed=True)

        self.main_layout.addWidget(self.main_widget)

def run():
    reload(solstice_accordion)
    SolsticePlayBlast.run()
