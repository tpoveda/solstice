#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_animmanager.py
# by Tomas Poveda
# ______________________________________________________________________
# ==================================================================="""

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows


class AnimManager(solstice_windows.Window, object):
    name = 'Solstice_AnimManager'
    title = 'Solstice Tools - Animation Manager'
    version = '1.0'

    def __init__(self):
        super(AnimManager, self).__init__()







        # solstice_project_folder = os.environ.get('SOLSTICE_PROJECT')
        # if not os.path.exists(solstice_project_folder):
        #     sp.update_solstice_project()
        #     solstice_project_folder = os.environ.get('SOLSTICE_PROJECT')
        # if solstice_project_folder and os.path.exists(solstice_project_folder):
        #     solstice_assets = os.path.join(solstice_project_folder, 'Asset')
        #     if os.path.exists(solstice_assets):
        #         anims = os.path.join(solstice_assets, 'AnimationLibrary')
        #         if os.path.exists(anims):
        #             self.pose_widget.setPath(anims)
        #         else:
        #             self.pose_widget.setPath(solstice_assets)
        #     else:
        #         self.pose_widget.setPath(solstice_project_folder)