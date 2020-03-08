#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains manager to Media related operations for Solstice
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging
from collections import OrderedDict

import fileseq
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.python import decorators, path as path_utils
from tpDcc.libs.qt.core import image

import artellapipe
from artellapipe.managers import media
from artellapipe.libs.ffmpeg.core import ffmpeglib

LOGGER = logging.getLogger()


class SolsticeMediaManager(media.MediaManager, object):
    def __init__(self):
        super(SolsticeMediaManager, self).__init__()

    def stamp_video(self, source, output, config_dict=None):
        print('stamping video ...')

    def stamp_image(self, source, output, config_dict=None):
        res_x = image.get_image_width(source)
        res_y = image.get_image_height(source)

        top_band = config_dict.get('top_band', None)
        bottom_band = config_dict.get('bottom_band', None)
        font_file = config_dict.get('text_font', 'Arial.ttf')
        font_family = config_dict.get('text_font_family', 'Regular')
        text_margin_x = config_dict.get('text_margin_x', 300)
        text_margin_y = config_dict.get('text_margin_y', 100)
        framecode = config_dict.get('framecode', '00:00:00:00')

        top_band_height = 0
        if top_band and os.path.isfile(top_band):
            top_band_height = image.get_image_height(top_band)
            res_y += top_band_height

        bottom_band_height = 0
        if bottom_band and os.path.isfile(bottom_band):
            bottom_band_height = image.get_image_height(bottom_band)
            res_y += bottom_band_height

        font_db = QFontDatabase()
        font_db.addApplicationFont(font_file)
        text_font = QFont(font_family)
        font_size = 32
        font_height = QFontMetrics(text_font).height()
        user = str(artellapipe.Tracker().get_user_name())
        shot_name = config_dict.get('shot_name', '') or ''
        task_name = config_dict.get('task_name', '') or ''
        task_comment = str(config_dict.get('task_comment', ''))
        fps = artellapipe.Tracker().get_project_fps()
        camera = str(config_dict.get('camera', 'No camera'))
        start_frame = str(config_dict.get('start_frame', None))
        focal_length = None
        if camera and tp.Dcc.object_exists(camera):
            focal_length = tp.Dcc.get_camera_focal_length(camera)

        sequence = fileseq.findSequenceOnDisk(source)
        frames_dict = OrderedDict()
        total_frames = len(sequence)
        for i in range(total_frames):
            sequence_frame = sequence[i]
            empty_frame_path = self._get_temp_file_path(sequence_frame, 'empty')
            empty_frame = image.create_empty_image(
                empty_frame_path, resolution_x=res_x, resolution_y=res_y, background_color=[92, 92, 92])
            frames_dict[sequence_frame] = empty_frame

        frame_outputs = dict()
        for i, (frame, empty_frame) in enumerate(frames_dict.items()):
            # Overlay playblast
            stream = ffmpeglib.overlay_image_to_video(empty_frame, frame, y=top_band_height)

            # Overlay top and bottom bands
            if top_band:
                stream = ffmpeglib.overlay_image_to_video(stream, top_band)
            if bottom_band:
                stream = ffmpeglib.overlay_image_to_video(stream, bottom_band, y=res_y - bottom_band_height)

            # Draw task and comment texts
            stream = ffmpeglib.draw_text(
                stream, task_name, x=40,
                y=text_margin_y + font_height, font_file=font_file, font_size=font_size)
            stream = ffmpeglib.draw_text(
                stream, task_comment, x=40,
                y=text_margin_y + (font_height * 2) + 25, font_file=font_file, font_size=font_size)

            # Draw frame
            current_frame = int(float(start_frame)) + i
            fps_text = '{} ({})'.format(current_frame, i + 1)
            stream = ffmpeglib.draw_text(
                stream, fps_text, x=40, y=res_y - font_height - text_margin_y - 70,
                font_file=font_file, font_size=font_size)

            # Draw camera name and focal length texts
            camera_text_width = QFontMetrics(text_font).width(camera)
            stream = ffmpeglib.draw_text(
                stream, camera, x=res_x / 2 - camera_text_width,
                y=res_y - font_height - text_margin_y - 70, font_file=font_file, font_size=font_size)
            fps_text = 'FPS: {}'.format(str(int(float(fps))))
            if focal_length:
                fps_text = ' Focal Length: {}'.format(focal_length)
            fps_focal_length_width = QFontMetrics(text_font).width(str(fps_text))
            stream = ffmpeglib.draw_text(
                stream, fps_text, x=res_x / 2 - fps_focal_length_width,
                y=res_y - font_height - text_margin_y - 20, font_file=font_file, font_size=font_size)

            # Draw user and shot texts
            user_text_width = QFontMetrics(text_font).width(user)
            shot_text_width = QFontMetrics(text_font).width(shot_name)
            user_shot_text_width = max(user_text_width, shot_text_width)
            stream = ffmpeglib.draw_text(
                stream, user, x=res_x - user_shot_text_width - text_margin_x,
                y=res_y - font_height - text_margin_y - 70, font_file=font_file, font_size=font_size)
            stream = ffmpeglib.draw_text(
                stream, shot_name, x=res_x - user_shot_text_width - text_margin_x,
                y=res_y - font_height - text_margin_y - 20, font_file=font_file, font_size=font_size)

            new_file_path = self._get_temp_file_path(empty_frame, 'main', index=i)
            frame_save = ffmpeglib.save_to_file(stream, new_file_path)
            frame_outputs[new_file_path] = frame_save

        if not frame_outputs:
            return

        frame_paths = frame_outputs.keys()
        frame_outs = frame_outputs.values()
        ffmpeglib.run_multiples_outputs_at_once(frame_outs)

        for frame_path in frame_paths:
            if not frame_path or not os.path.isfile(frame_path):
                LOGGER.warning('Some frames were not generated properly. Aborting operation ...')
                return

        video_file_path = self._get_temp_file_path(source, 'video')
        if not video_file_path.endswith('.mov'):
            video_file_path_split = os.path.splitext(video_file_path)
            video_file_path = '{}.mov'.format(video_file_path_split[0])
        ffmpeglib.create_video_from_sequence_file(frame_paths[0], video_file_path)
        if not os.path.isfile(video_file_path):
            LOGGER.error('Error while stamping playblast video ...')
            return

        draw_timestamp_stream = ffmpeglib.draw_timestamp_on_video(
            video_file_path, text='Time: ', x=40, y=res_y - font_height - text_margin_y - 20,
            font_file=font_file, font_size=font_size, timecode_rate=fps, timecode=framecode)
        ffmpeglib.save_to_file(draw_timestamp_stream, output, run_stream=True)

        return output

    def _get_temp_file_path(self, file_path, suffix=None, index=None, padding=4):
        if not suffix:
            suffix = 'new'
        file_path_dir = os.path.dirname(file_path)
        file_path_name = os.path.basename(file_path)
        file_path_split = file_path_name.split('.')
        new_file_path = '{}_{}'.format(file_path_split[0], suffix)
        if index is not None:
            new_index = str(index).zfill(padding)
            new_file_path = '{}.{}'.format(new_file_path, new_index)
        else:
            if len(file_path_split) > 2:
                new_file_path = '{}.{}'.format(new_file_path, file_path_split[1])
        temp_file_path = path_utils.clean_path(
            os.path.join(file_path_dir, '{}.{}'.format(new_file_path, file_path_split[-1])))

        return temp_file_path


@decorators.Singleton
class SolsticeMediaManagerSingleton(SolsticeMediaManager, object):
    def __init__(self):
        SolsticeMediaManager.__init__(self)


artellapipe.register.register_class('MediaMgr', SolsticeMediaManagerSingleton)
