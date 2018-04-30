#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_publisher.py
# by Tomas Poveda
# Tool that is used to publish assets and sequences
# ______________________________________________________________________
# ==================================================================="""

from solstice_gui import solstice_windows


class SolsticePublisher(solstice_windows.Window, object):

    name = 'Publisher'
    title = 'Solstice Tools - Publisher'
    version = '1.0'
    docked = False

    def __init__(self, name='PublisherWindow', parent=None, **kwargs):
        super(SolsticePublisher, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticePublisher, self).custom_ui()

        self.set_logo('solstice_publisher_logo')


def run():
    SolsticePublisher().run()