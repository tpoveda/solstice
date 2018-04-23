#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_shadermanager.py
# by Tomas Poveda
# Tool used to manage all shaders used by all the assets in the short film
# ______________________________________________________________________
# ==================================================================="""

from Qt.QtCore import *
from Qt.QtWidgets import *

from solstice_gui import solstice_windows


class ShaderManager(solstice_windows.Window, object):

    title = 'Solstice Tools - Shader Manager'
    version = '1.0'
    docked = False

    def __init__(self, name='ShaderManagerWindow', parent=None, **kwargs):
        super(ShaderManager, self).__init__(name=name, parent=parent, **kwargs)

    def custom_ui(self):
        super(ShaderManager, self).custom_ui()




def run():
    ShaderManager.run()
