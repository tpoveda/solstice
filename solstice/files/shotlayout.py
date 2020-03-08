#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementations for masater layout sequence files
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging
import traceback

import tpDcc as tp
from tpDcc.libs.python import fileio

import artellapipe
from artellapipe.core import shotfile

LOGGER = logging.getLogger()


class SolsticeShotLayoutFile(shotfile.ArtellaShotFile, object):
    def __init__(self, shot=None):
        super(SolsticeShotLayoutFile, self).__init__(file_shot=shot)

    def _open_file(self, file_path):
        if file_path and os.path.isfile(file_path):
            tp.Dcc.open_file(file_path)

    def _export_file(self, file_path, *args, **kwargs):

        # Retrieve master layout file path
        sequence_name = self._shot.get_sequence()
        if not sequence_name:
            LOGGER.warning('Impossible to export shot file "{}" because is not linked to any sequence!'.format(
                self._shot.get_name())
            )
            return None
        sequence = artellapipe.SequencesMgr().find_sequence(sequence_name)
        if not sequence:
            LOGGER.warning(
                'Impossible to export shot file "{}" because sequence "{}" was not found in current project'.format(
                    self._shot.get_name(), sequence_name))
            return None
        sequence_file_type = sequence.get_file_type('master')
        if not sequence_file_type:
            LOGGER.warning(
                'Impossible to export shot file "{}" because sequence file type "master" is not defined '
                'in current project'.format(self._shot.get_name()))
            return None

        master_file_path = sequence_file_type.get_file()
        if not master_file_path or not os.path.exists(master_file_path):
            LOGGER.warning(
                'Impossible to export shot file "{}" because master layout file "{}" does not exists!'.format(
                    self._shot.get_name(), master_file_path))
            return None

        sequence_file_type.open_file()

        master_locked = False
        if os.path.isfile(master_file_path):
            valid_lock = artellapipe.FilesMgr().lock_file(master_file_path)
            master_locked = True
            if not valid_lock:
                LOGGER.warning('Was not possible to lock file: {}'.format(master_file_path))
                return False

        sequence_file_type.open_file()

        file_path_name = os.path.basename(file_path)
        file_path_dir = os.path.dirname(file_path)
        if not os.path.isdir(file_path_dir):
            LOGGER.info('Creating export file path directory: {}'.format(file_path_dir))
            try:
                os.makedirs(file_path_dir)
            except Exception as exc:
                LOGGER.error(
                    'Error while creating export path directory: "{}" | {} | {}'.format(
                        file_path_dir, exc, traceback.format_exc()))
                return None

        try:
            if os.path.isfile(file_path):
                fileio.delete_file(file_path_name, file_path_dir)
            fileio.copy_file(master_file_path, file_path)
            LOGGER.info('Created new Shot File: {}'.format(file_path))
        except Exception as exc:
            LOGGER.error(
                'Error while copying shot file "{}" from master layout file "{}" | {} | {}'.format(
                    file_path, master_file_path, exc, traceback.format_exc()))
            return None

        if os.path.isfile(file_path):
            valid_lock = artellapipe.FilesMgr().lock_file(file_path)
            if not valid_lock:
                LOGGER.warning('Was not possible to lock file: {}'.format(file_path))

        tp.Dcc.open_file(file_path)

        shot_anim_file_type = self._shot.get_file_type('shot_layout_anim')
        if not shot_anim_file_type:
            LOGGER.warning(
                'Impossible to export shot "{}" because shot file type "shot_layout_anim" is not defined '
                'in current project'.format(self._shot.get_name()))
            return None

        start_frame = kwargs.get('start_frame', 101)
        valid_anim_export = shot_anim_file_type.export_file(start_frame=start_frame)
        if not valid_anim_export:
            LOGGER.warning('Layout Animation Export was not exported in file!')
            return None

        if master_locked:
            artellapipe.FilesMgr().unlock_file(master_file_path, warn_user=False)

        try:
            shot_anim_file_path = shot_anim_file_type.get_file()
            shot_anim_file_path_name = os.path.basename(shot_anim_file_path)
            shot_anim_file_path_directory = os.path.dirname(shot_anim_file_path)
            fileio.delete_file(shot_anim_file_path_name, shot_anim_file_path_directory)
        except Exception as exc:
            LOGGER.warning(
                'Was not possible to remove Shot Layout Animation File: "{}" | {} | {}. Remove it manually'.format(
                    shot_anim_file_path, exc, traceback.format_exc()))

        try:
            tp.Dcc.convert_fraction_keys_to_whole_keys(consider_selected_range=False)
        except Exception as exc:
            LOGGER.warning(
                'Could not resolve any keyframes on fractions of a frame: {} | {}'.format(exc, traceback.format_exc()))

        # Clean shot nodes that are not valid anymore
        all_shots = tp.Dcc.all_scene_shots()
        shots_to_delete = [shot for shot in all_shots if shot != self.get_name()]
        tp.Dcc.delete_object(shots_to_delete)

        # Update timeline
        start_offset = self._shot.get_start_frame() - start_frame
        start_frame = self._shot.get_start_frame() - start_offset
        end_frame = self._shot.get_end_frame() - start_offset
        tp.Dcc.set_active_frame_range(start_frame, end_frame)

        # Update shot attributes
        self._shot.set_start_frame(start_frame)
        self._shot.set_end_frame(end_frame)

        # Remove cameras that does not belong to the shot
        camera_name = self._shot.get_camera()
        root_node = None
        all_cameras = tp.Dcc.get_all_cameras(full_path=True) or list()
        for camera in all_cameras:
            if not camera:
                continue
            base_name = tp.Dcc.node_short_name(camera)
            if base_name == camera_name:
                root_node = camera.split('|')[1]
                break
        if root_node:
            for camera in all_cameras:
                if not camera:
                    continue
                base_name = tp.Dcc.node_short_name(camera)
                if base_name == camera_name:
                    continue
                reps = 0
                node_to_delete = camera
                camera_parent = tp.Dcc.node_parent(camera)
                while camera_parent != '|{}'.format(root_node) and reps < 10:
                    node_to_delete = camera_parent
                    camera_parent = tp.Dcc.node_parent(node_to_delete)
                    reps += 1
                tp.Dcc.delete_object(node_to_delete)
        else:
            for camera in all_cameras:
                if not camera:
                    continue
                base_name = tp.Dcc.node_short_name(camera)
                if base_name == camera_name:
                    continue
                tp.Dcc.delete_object(camera)

        # Force look through to shot camera
        tp.Dcc.look_through_camera(camera_name)

        # Save scene
        tp.Dcc.save_current_scene(force=True)
        if tp.is_maya():
            from tpDcc.dccs.maya.core import helpers
            helpers.clean_student_line()

        return True


class SolsticeShotAnimationLayoutFile(shotfile.ArtellaShotFile, object):
    def __init__(self, shot=None):
        super(SolsticeShotAnimationLayoutFile, self).__init__(file_shot=shot)

    def _export_file(self, file_path, *args, **kwargs):

        if not file_path:
            return

        start_frame = kwargs.get('start_frame', 101)

        if os.path.isfile(file_path):
            valid_lock = artellapipe.FilesMgr().lock_file(file_path)
            if not valid_lock:
                LOGGER.warning('Was not possible to lock file: {}'.format(file_path))

        valid_anim_export = self._shot.export_animation(file_path)
        valid_anim_import = self._shot.import_animation(file_path, start_frame=start_frame)

        return valid_anim_export and valid_anim_import
