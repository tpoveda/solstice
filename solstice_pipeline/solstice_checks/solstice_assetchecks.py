#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_assetchecks.py
# by Tomas Poveda
# Module that contains checks related with assets
# ______________________________________________________________________
# ==================================================================="""

import solstice_pipeline as sp
from solstice_pipeline.solstice_checks import solstice_task


class NotLockedAsset(solstice_task.SanityTask, object):
    def __init__(self, asset, file_type, status='working', auto_fix=False, parent=None):
        super(NotLockedAsset, self).__init__(name='Asset {0} {1} file is not locked'.format(status, file_type), auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self._status = status
        self._file_type = file_type
        self.set_task_text('Check if asset file is not locked')

    def check(self):
        current_user_can_unlock = self._asset().is_locked(self._file_type, status=self._status)[1]
        if not current_user_can_unlock:
            error_message = 'Asset {0} | {1} {2} file is locked!'.format(self._asset().name, self._status, self._file_type)
            sp.logger.debug(error_message)
            self.set_error_message(error_message)
            return False

        return True

    def fix(self):
        pass


class ValidPublishedTextures(solstice_task.SanityTask, object):
    def __init__(self, asset, auto_fix=False, parent=None):
        super(ValidPublishedTextures, self).__init__(name='Valid Published Textures Check', auto_fix=auto_fix, parent=parent)

        self._asset = asset
        self.set_task_text('Check if asset has valid textures published')

    def check(self):
        published_textures_info = self._asset().get_max_versions(status='published', categories=['textures'])['server']
        if not published_textures_info or published_textures_info['textures'] is None:
            error_message = 'Asset {} has not textures published yet! Before publishing shading files you need to publish textures!'.format(self._asset().name)
            sp.logger.debug(error_message)
            self.set_error_message(error_message)
            return False

        return True

    def fix(self):
        pass
