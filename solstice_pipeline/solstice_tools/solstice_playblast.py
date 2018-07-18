#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Tool to capture Playblast for Solstice Short Film
# ==================================================================="""

import os
import re
import sys
import glob
import json
import tempfile
import contextlib
from functools import partial

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_label, solstice_accordion, solstice_sync_dialog
from solstice_pipeline.solstice_utils import solstice_maya_utils as utils
from solstice_pipeline.solstice_utils import solstice_python_utils as python
from solstice_pipeline.resources import solstice_resource


class TimeRanges(object):
    RANGE_TIME_SLIDER = 'Time Slider'
    RANGE_START_END = 'Start/End'
    CURRENT_FRAME = 'Current Frame'
    CUSTOM_FRAMES = 'Custom Frames'


class ScaleSettings(object):
    SCALE_WINDOW = 'From Window'
    SCALE_RENDER_SETTINGS = 'From Render Settings'
    SCALE_CUSTOM = 'Custom'


class SolsticePlayblastWidget(QWidget, object):

    id = 'DefaultPlayblastWidget'

    label = ''
    labelChanged = Signal(str)
    optionsChanged = Signal()

    def __init__(self, parent=None):
        super(SolsticePlayblastWidget, self).__init__(parent=parent)

        self.custom_ui()
        self.setup_signals()

    def __str__(self):
        return self.label or type(self).__name__

    def __repr__(self):
        return u"%s.%s(%r)" % (__name__, type(self).__name__, self.__str__())

    id = python.classproperty(lambda cls: cls.__name__)

    def get_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        return layout

    def custom_ui(self):
        self.main_layout = self.get_main_layout()
        self.setLayout(self.main_layout)

    def setup_signals(self):
        pass

    def validate(self):
        """
        Will ensure that widget outputs are valid and will raise proper errors if necessary
        :return: list<str>
        """

        return []

    def initialize(self):
        """
        Method used to initialize callbacks on widget
        """

        pass

    def uninitialize(self):
        """
        Un-register any callback created when deleting the widget
        """

        pass

    def get_outputs(self):
        """
        Returns the outputs variables of the Playblast widget as dict
        :return: dict
        """

        return {}

    def get_inputs(self, as_preset=False):
        """
        Returns a dict with proper input variables as keys of the dictionary
        :return: dict
        """

        return {}

    def apply_inputs(self, attrs_dict):
        """
        Applies the given dict of attributes to the widget
        :param attrs_dict: dict
        """

        pass

    def on_playblast_finished(self, options):
        pass


class SolsticeTimeRange(SolsticePlayblastWidget, object):

    id = 'Time Range'
    label = 'Time Range'

    def __init__(self, parent=None):
        super(SolsticeTimeRange, self).__init__(parent=parent)

        self._event_callbacks = list()

    def get_main_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        return layout

    def custom_ui(self):
        super(SolsticeTimeRange, self).custom_ui()

        self.mode = QComboBox()
        self.mode.addItems([TimeRanges.RANGE_TIME_SLIDER, TimeRanges.RANGE_START_END, TimeRanges.CURRENT_FRAME, TimeRanges.CUSTOM_FRAMES])

        self.start = QSpinBox()
        self.start.setRange(-sys.maxint, sys.maxint)
        self.start.setFixedHeight(20)
        self.end = QSpinBox()
        self.end.setRange(-sys.maxint, sys.maxint)
        self.end.setFixedHeight(20)

        self.custom_frames = QLineEdit()
        self.custom_frames.setFixedHeight(20)
        self.custom_frames.setPlaceholderText('Example: 1-20,25,50,75,100-150')
        self.custom_frames.setVisible(True)
        self.custom_frames.setVisible(False)

        for widget in [self.mode, self.start, self.end, self.custom_frames]:
            self.main_layout.addWidget(widget)

    def setup_signals(self):
        self.start.valueChanged.connect(self._ensure_end)
        self.start.valueChanged.connect(self._on_mode_changed)
        self.end.valueChanged.connect(self._ensure_start)
        self.end.valueChanged.connect(self._on_mode_changed)
        self.mode.currentIndexChanged.connect(self._on_mode_changed)
        self.custom_frames.textChanged.connect(self._on_mode_changed)

    def get_inputs(self, as_preset=False):
        return {
            'time': self.mode.currentText(),
            'start_frame': self.start.value(),
            'end_frame': self.end.value(),
            'frame': self.custom_frames.text()
        }

    def get_outputs(self):
        mode = self.mode.currentText()
        frames = None
        if mode == TimeRanges.RANGE_TIME_SLIDER:
            start, end = utils.get_time_slider_range()
        elif mode == TimeRanges.RANGE_START_END:
            start = self.start.value()
            end = self.end.value()
        elif mode == TimeRanges.CURRENT_FRAME:
            frame = utils.get_current_frame()
            start = frame
            end = frame
        elif mode == TimeRanges.CUSTOM_FRAMES:
            frames = self.parse_frames(self.custom_frames.text())
            start = None
            end = None
        else:
            raise NotImplementedError('Unsupported time range mode: "{}"'.format(mode))

        return {
            'start_frame': start,
            'end_frame': end,
            'frame': frames
        }

    def apply_inputs(self, attrs_dict):
        mode = self.mode.findText(attrs_dict.get('time', TimeRanges.RANGE_TIME_SLIDER))
        start_frame = attrs_dict.get('start_frame', 1)
        end_frame = attrs_dict.get('end_frame', 120)
        custom_frames = attrs_dict.get('frame', None)

        self.mode.setCurrentIndex(mode)
        self.start.setValue(int(start_frame))
        self.end.setValue(int(end_frame))
        if custom_frames is not None:
            self.custom_frames.setText(custom_frames)

    def _ensure_start(self, value):
        self.start.setValue(min(self.start.value(), value))

    def _ensure_end(self, value):
        self.end.setValue(max(self.end.value(), value))

    def _on_mode_changed(self, emit=True):
        mode = self.mode.currentText()
        if mode == TimeRanges.RANGE_TIME_SLIDER:
            start, end = utils.get_time_slider_range()
            self.start.setEnabled(False)
            self.end.setEnabled(False)
            self.start.setVisible(True)
            self.end.setVisible(True)
            self.custom_frames.setVisible(False)
            mode_values = int(start), int(end)
        elif mode == TimeRanges.RANGE_START_END:
            self.start.setEnabled(True)
            self.end.setEnabled(True)
            self.start.setVisible(True)
            self.end.setVisible(True)
            self.custom_frames.setVisible(False)
            mode_values = self.start.value(), self.end.value()
        elif mode == TimeRanges.CUSTOM_FRAMES:
            self.start.setVisible(False)
            self.end.setVisible(False)
            self.custom_frames.setVisible(True)
            mode_values = '({})'.format(self.custom_frames.text())
            self.validate()
        else:
            self.start.setEnabled(False)
            self.end.setEnabled(False)
            self.start.setVisible(True)
            self.end.setVisible(True)
            self.custom_frames.setVisible(False)
            current_frame = int(utils.get_current_frame())
            mode_values = '({})'.format(current_frame)

        self.label = 'Time Range {}'.format(mode_values)
        self.labelChanged.emit(self.label)

    def validate(self):
        errors = list()
        if self.mode.currentText() == TimeRanges.CUSTOM_FRAMES:
            self.custom_frames.setStyleSheet('')
            try:
                self.parse_frames(self.custom_frames.text())
            except ValueError as e:
                errors.append('{0} : Invalid frame description: "{1}"'.format(self.id, e))
                self.custom_frames.setStyleSheet('border 1px solid red;')
            except Exception:
                pass

        return errors

    @staticmethod
    def parse_frames(frames_str):
        """
        Parses the given frames from a frame list string
        :param frames_str: parse_frames("0-3;30") --> [0, 1, 2, 3, 30]
        :return: list<str>
        """

        result = list()
        if not frames_str.strip():
            raise ValueError('Cannot parse an empty frame string')
        if not re.match("^[-0-9,; ]*$", frames_str):
            raise ValueError('Invalid symbols in frame string: {}'.format(frames_str))

        for raw in re.split(';|,', frames_str):
            value = raw.strip().replace(' ', '')
            if not value:
                continue

            # Check for sequences (1-20) including negatives (-10--8)
            sequence = re.search("(-?[0-9]+)-(-?[0-9]+)", value)
            if sequence:
                start, end = sequence.groups()
                frames = range(int(start), int(end) + 1)
                result.extend(frames)
            else:
                try:
                    frame = int(value)
                except ValueError:
                    raise ValueError('Invalid frame description: "{}"'.format(value))
                result.append(frame)

        if not result:
            raise ValueError('Unable to parse any frame from string: {}'.format(frames_str))

        return result

    def initialize(self):
        self._register_callbacks()

    def uninitialize(self):
        self._remove_callbacks()

    def _register_callbacks(self):
        """
        Register Maya time and playback range change callbacks
        """

        callback = lambda x: self._on_mode_changed(emit=False)
        current_frame = OpenMaya.MEventMessage.addEventCallback('timeChanged', callback)
        time_range = OpenMaya.MEventMessage.addEventCallback('playbackRangeChanged', callback)
        self._event_callbacks.append(current_frame)
        self._event_callbacks.append(time_range)

    def _remove_callbacks(self):
        for callback in self._event_callbacks:
            try:
                OpenMaya.MEventMessage.removeCallback(callback)
            except RuntimeError as e:
                sp.logger.error('Encounter error: {}'.format(e))


class SolsticeCameras(SolsticePlayblastWidget, object):
    """
    Allows user to select the camera to generate playblast from
    """

    id = 'Camera'

    def __init__(self, parent=None):
        super(SolsticeCameras, self).__init__(parent=parent)

        self._on_set_active_camera()
        self._on_update_label()

    def get_main_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        return layout

    def custom_ui(self):
        super(SolsticeCameras, self).custom_ui()

        self.cameras = QComboBox()
        self.cameras.setMinimumWidth(200)

        self.get_active = QPushButton('Get Active')
        self.get_active.setToolTip('Set camera from currently active view')
        self.refresh = QPushButton('Refresh')
        self.refresh.setToolTip('Refresh the list of cameras')

        for widget in [self.cameras, self.get_active, self.refresh]:
            self.main_layout.addWidget(widget)

    def setup_signals(self):
        self.get_active.clicked.connect(self._on_set_active_camera)
        self.refresh.clicked.connect(self._on_refresh)
        self.cameras.currentIndexChanged.connect(self._on_update_label)
        self.cameras.currentIndexChanged.connect(self.validate)

    def validate(self):
        errors = list()
        camera = self.cameras.currentText()
        if not cmds.objExists(camera):
            errors.append('{0} : Selected Camera "{1}" does not exists!'.format(self.id, camera))
            self.cameras.setStyleSheet('border 1px solid red;')
        else:
            self.cameras.setStyleSheet('')

        return errors

    def get_outputs(self):
        """
        Returns the current selected camera
        :return: str
        """

        camera_id = self.cameras.currentIndex()
        camera = str(self.cameras.itemText(camera_id)) if camera_id != -1 else None

        return {'camera': camera}

    def select_camera(self, camera):
        if camera:
            cameras = cmds.ls(camera, long=True)
            if not cameras:
                return
            camera = cameras[0]
            for i in range(self.cameras.count()):
                value = str(self.cameras.itemText(i))
                if value == camera:
                    self.cameras.setCurrentIndex(i)
                    return

    def _on_set_active_camera(self):
        camera = utils.get_current_camera()
        self._on_refresh(camera=camera)
        # if cmds.objExists(camera):
        #     cmds.select(camera)

    def _on_update_label(self):
        camera = self.cameras.currentText()
        camera = camera.split('|', 1)[-1]
        self.label = 'Camera ({})'.format(camera)
        self.labelChanged.emit(self.label)

    def _on_refresh(self, camera=None):
        """
        Refresh of current cameras in the scene and emit proper signal if necessary
        :param camera: str, if camera nave is given, it will try to select this camera after refresh
        """

        cam = self.get_outputs()['camera']
        if camera is None:
            index = self.cameras.currentIndex()
            if index != -1:
                camera = self.cameras.currentIndex()

        self.cameras.blockSignals(True)
        try:
            self.cameras.clear()
            camera_shapes = cmds.ls(type='camera')
            camera_transforms = cmds.listRelatives(camera_shapes, parent=True, fullPath=True)
            self.cameras.addItems(camera_transforms)
            self.select_camera(camera)
            self.cameras.blockSignals(False)
        except Exception as e:
            self.cameras.blockSignals(False)
            sp.logger.debug(str(e))

        if cam != self.get_outputs()['camera']:
            camera_index = self.cameras.currentIndex()
            self.cameras.currentIndexChanged.emit(camera_index)


class SolsticeResolution(SolsticePlayblastWidget, object):

    id = 'Resolution'

    resolutionChanged = Signal()

    def __init__(self, parent=None):
        super(SolsticeResolution, self).__init__(parent=parent)

    def get_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def custom_ui(self):
        super(SolsticeResolution, self).custom_ui()

        self.mode = QComboBox()
        self.mode.addItems([ScaleSettings.SCALE_WINDOW, ScaleSettings.SCALE_RENDER_SETTINGS, ScaleSettings.SCALE_CUSTOM])
        self.mode.setCurrentIndex(1)

        self.resolution = QWidget()
        resolution_layout = QHBoxLayout()
        resolution_layout.setContentsMargins(0, 0, 0, 0)
        resolution_layout.setSpacing(6)
        self.resolution.setLayout(resolution_layout)

        width_lbl = QLabel('Width')
        width_lbl.setFixedWidth(40)
        self.width = QSpinBox()
        self.width.setMinimum(0)
        self.width.setMaximum(99999)
        self.width.setValue(1920)

        height_lbl = QLabel('Height')
        height_lbl.setFixedWidth(40)
        self.height = QSpinBox()
        self.height.setMinimum(0)
        self.height.setMaximum(99999)
        self.height.setValue(1080)

        resolution_layout.addWidget(width_lbl)
        resolution_layout.addWidget(self.width)
        resolution_layout.addWidget(height_lbl)
        resolution_layout.addWidget(self.height)

        self.scale_result = QLineEdit()
        self.scale_result.setReadOnly(True)

        self.percent_layout = QHBoxLayout()
        self.percent_lbl = QLabel('Scale')
        self.percent = QDoubleSpinBox()
        self.percent.setMinimum(0.01)
        self.percent.setSingleStep(0.05)
        self.percent.setValue(1.0)
        self.percent_presets_layout = QHBoxLayout()
        self.percent_presets_layout.setSpacing(4)
        for value in [0.25, 0.5, 0.75, 1.0, 2.0]:
            btn = QPushButton(str(value))
            self.percent_presets_layout.addWidget(btn)
            btn.setFixedWidth(35)
            btn.clicked.connect(partial(self.percent.setValue, value))
        self.percent_layout.addWidget(self.percent_lbl)
        self.percent_layout.addWidget(self.percent)
        self.percent_layout.addLayout(self.percent_presets_layout)

        self.main_layout.addWidget(self.mode)
        self.main_layout.addWidget(self.resolution)
        self.main_layout.addLayout(self.percent_layout)
        self.main_layout.addWidget(self.scale_result)


class SolsticeCodec(SolsticePlayblastWidget, object):

    id = 'Codec'
    label = 'Codec'

    def __init__(self, parent=None):
        super(SolsticeCodec, self).__init__(parent=parent)

    def get_main_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def custom_ui(self):
        super(SolsticeCodec, self).custom_ui()

        self.format = QComboBox()
        self.compression = QComboBox()
        self.quality = QSpinBox()
        self.quality.setMinimum(0)
        self.quality.setMaximum(100)
        self.quality.setValue(100)
        self.quality.setToolTip('Compression quality percentage')

        for widget in [self.format, self.compression, self.quality]:
            self.main_layout.addWidget(widget)

        # This need to be added here so when we do the first refresh the compression list is updated properly
        self.format.currentIndexChanged.connect(self._on_format_changed)

        self.refresh()

        index = self.format.findText('qt')
        if index != -1:
            self.format.setCurrentIndex(index)
            index = self.compression.findText('H.264')
            if index != -1:
                self.compression.setCurrentIndex(index)

    def setup_signals(self):
        self.compression.currentIndexChanged.connect(self.optionsChanged)
        self.format.currentIndexChanged.connect(self.optionsChanged)
        self.quality.valueChanged.connect(self.optionsChanged)

    def get_inputs(self, as_preset=False):
        return self.get_outputs()

    def apply_inputs(self, attrs_dict):
        codec_format = attrs_dict.get('format', 0)
        compression = attrs_dict.get('compression', 4)
        quality = attrs_dict.get('quality', 100)

        self.format.setCurrentIndex(self.format.findText(codec_format))
        self.compression.setCurrentIndex(self.compression.findText(compression))
        self.quality.setValue(int(quality))

    def get_outputs(self):
        return {'format': self.format.currentText(), 'compression': self.compression.currentText(), 'quality': self.quality.value()}

    def refresh(self):
        self.format.clear()
        self.format.addItems(sorted(utils.get_playblast_formats()))

    def _on_format_changed(self):
        """
        Refresh available compressions
        """

        format = self.format.currentText()
        self.compression.clear()
        self.compression.addItems(utils.get_playblast_compressions(format=format))


class DefaultPlayblastOptions(SolsticePlayblastWidget, object):

    def get_outputs(self):
        outputs = dict()
        scene = parse_current_scene()
        outputs['sound'] = scene['sound']
        outputs['show_ornaments'] = True
        outputs['camera_options'] = dict()
        outputs['camera_options']['overscan'] = 1.0
        outputs['camera_options']['displayFieldChart'] = False
        outputs['camera_options']['displayFilmGate'] = False
        outputs['camera_options']['displayFilmOrigin'] = False
        outputs['camera_options']['displayFilmPivot'] = False
        outputs['camera_options']['displayGateMask'] = False
        outputs['camera_options']['displayResolution'] = False
        outputs['camera_options']['displaySafeAction'] = False
        outputs['camera_options']['displaySafeTitle'] = False

        return outputs


class BasePlayblastOptions(SolsticePlayblastWidget, object):

    id = 'Options'
    label = 'Options'

    def __init__(self, parent=None):
        super(BasePlayblastOptions, self).__init__(parent=parent)

    def get_main_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def custom_ui(self):
        super(BasePlayblastOptions, self).custom_ui()

        self.isolate_view = QCheckBox('Use isolate view from active panel')
        self.off_screen = QCheckBox('Render offscreen')

        for widget in [self.isolate_view, self.off_screen]:
            self.main_layout.addWidget(widget)

        self.widgets = {
            'off_screen': self.off_screen,
            'isolate_view': self.isolate_view
        }

    def setup_signals(self):
        self.isolate_view.stateChanged.connect(self.optionsChanged)
        self.off_screen.stateChanged.connect(self.optionsChanged)

    def get_defaults(self):
        return {
            'off_screen': True,
            'isolate_view': False
        }

    def get_inputs(self, as_preset=False):
        inputs = dict()
        for key, widget in self.widgets.items():
            state = widget.isChecked()
            inputs[key] = state

        return inputs


class PlayblastPreview(QWidget, object):
    """
    Playtblast image preview
    """

    __DEFAULT_WIDTH__ = 320
    __DEFAULT_HEIGHT__ = 180

    def __init__(self, options, validator, parent=None):
        super(PlayblastPreview, self).__init__(parent=parent)

        self.options = options
        self.validator = validator
        self.preview = solstice_label.ClickLabel()
        self.preview.setFixedWidth(self.__DEFAULT_WIDTH__)
        self.preview.setFixedHeight(self.__DEFAULT_HEIGHT__)

        tip = 'Click to refresh playblast preview'
        self.preview.setToolTip(tip)
        self.preview.setStatusTip(tip)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.layout.addWidget(self.preview)

        self.preview.clicked.connect(self.refresh)

    def showEvent(self, event):
        self.refresh()
        event.accept()

    def refresh(self):
        """
        Refresh playblast preview
        """

        frame = cmds.currentTime(query=True)

        # When play blasting outside of an undo queue next undo will trigger a reset to frame 0
        # To solve this and ensure undo works properly, we update undo queue with current time
        cmds.currentTime(frame, update=True)

        valid = self.validator()
        if not valid:
            return

        with utils.maya_no_undo():
            options = self.options()
            tempdir = tempfile.mkdtemp()

            # Override settings that are constants for the preview
            options = options.copy()
            options['filename'] = None
            options['complete_filename'] = os.path.join(tempdir, 'temp.jpg')
            options['width'] = self.__DEFAULT_WIDTH__
            options['height'] = self.__DEFAULT_HEIGHT__
            options['viewer'] = False
            options['frame'] = frame
            options['off_screen'] = True
            options['format'] = 'image'
            options['compression'] = 'jpg'
            options['sound'] = None

            frame_name = capture(**options)
            if not frame_name:
                sp.logger.warning('Preview failed!')
                return

            image = QPixmap(frame_name)
            self.preview.setPixmap(image)
            os.remove(frame_name)


class PlayblastPreset(QWidget, object):

    presetLoaded = Signal(dict)
    configOpened = Signal()

    id = 'Presets'
    label = 'Presets'

    registered_paths = list()

    def __init__(self, inputs_getter, parent=None):
        super(PlayblastPreset, self).__init__(parent=parent)

        self.inputs_getter = inputs_getter

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.presets = QComboBox()
        self.presets.setFixedWidth(220)
        self.presets.addItem('*')

        save_icon = solstice_resource.icon('save')
        self.save = QPushButton()
        self.save.setIcon(save_icon)
        self.save.setFixedWidth(30)
        self.save.setToolTip('Save Preset')
        self.save.setStatusTip('Save Preset')

        load_icon = solstice_resource.icon('open')
        self.load = QPushButton()
        self.load.setIcon(load_icon)
        self.load.setFixedWidth(30)
        self.load.setToolTip('Load Preset')
        self.load.setStatusTip('Load Preset')

        preset_config_icon = solstice_resource.icon('config')
        self.preset_config = QPushButton()
        self.preset_config.setIcon(preset_config_icon)
        self.preset_config.setFixedWidth(30)
        self.preset_config.setToolTip('Preset Configuration')
        self.preset_config.setStatusTip('Preset Configuration')

        for widget in [self.presets, self.save, self.load, self.preset_config]:
            layout.addWidget(widget)

        self.save.clicked.connect(self._on_save_preset)
        self.load.clicked.connect(self.import_preset)
        self.preset_config.clicked.connect(self.configOpened)
        self.presets.currentIndexChanged.connect(self.load_active_preset)

        solstice_presets_folder = os.path.normpath(os.path.join(sp.get_solstice_project_path(), 'Assets', 'Scripts', 'PIPELINE', '__working__', 'PlayblastPresets'))
        if not os.path.exists(solstice_presets_folder):
            sp.logger.debug('Solstice Presets Path not found! Trying to sync through Artella!')
            solstice_sync_dialog.SolsticeSyncPath(paths=[os.path.dirname(os.path.dirname(solstice_presets_folder))]).sync()
        self.register_preset_path(solstice_presets_folder)

        self._process_presets()

    def get_inputs(self, as_preset=False):
        if as_preset:
            return {}
        else:
            current_index = self.presets.currentIndex()
            selected = self.presets.itemData(current_index)
            return {'selected': selected}

    def apply_inputs(self, settings):
        path = settings.get('selected', None)
        index = self.presets.findData(path)
        if index == -1:
            if os.path.exists(path):
                sp.logger.info('Adding previously selected preset explicitily: {}'.format(path))
                self.add_preset(path)
            else:
                sp.logger.warning('Previously selected preset is not available: {}'.format(path))
                index = 0

        self.presets.setCurrentIndex(index)

    @classmethod
    def get_preset_paths(cls):
        """
        Returns existing registered preset paths
        :return: list<str>, list of full paths
        """

        paths = list()
        for path in cls.registered_paths:
            if path in paths:
                continue
            if not os.path.exists(path):
                continue
            paths.append(path)

        return paths

    @classmethod
    def register_preset_path(cls, path):
        """
        Add file path to registered presets
        :param path: str, path of the preset file
        """

        if path in cls.registered_paths:
            sp.logger.warning('Preset path already registered: "{}"'.format(path))
            return
        cls.registered_paths.append(path)

        return path

    @classmethod
    def discover_presets(cls, paths=None):
        """
        Get the full list of files found in the registered preset folders
        :param paths: list<str>, directories which stores preset files
        :return: list<str>, valid JSON preset file paths
        """

        presets = list()
        for path in paths or cls.get_preset_paths():
            path = os.path.normpath(path)
            if not os.path.isdir(path):
                continue

            glob_query = os.path.abspath(os.path.join(path, '*.json'))
            file_names = glob.glob(glob_query)
            for file_name in file_names:
                if file_name.startswith('_'):
                    continue
                if not python.file_has_info(file_name):
                    sp.logger.warning('File size is smaller than 1 byte for preset file: "{}"'.format(file_name))
                    continue
                if file_name not in presets:
                    presets.append(file_name)

        return presets

    def get_presets(self):
        """
        Returns all currently listed presets
        :return: list<str>
        """

        presets_list = [self.presets.itemText(i) for i in range(self.presets.count())]
        return presets_list

    def add_preset(self, filename):
        pass

    def import_preset(self):
        """
        Load preset file sto override output values
        """

        path = self._default_browse_path()
        filters = 'Text file (*.json)'
        dialog = QFileDialog()
        filename, _ = dialog.getOpenFileName(self, 'Open Playblast Preset File', path, filters)
        if not filename:
            return

        self.add_preset(filename)

        return self.load_active_preset()

    def save_preset(self, inputs):
        """
        Save Playblast template on a file
        :param inputs: dict
        """

        path = self._default_browse_path()
        filters = 'Text file (*.json)'
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Playblast Preset File', path, filters)
        if not filename:
            return

        with open(filename, 'w') as f:
            json.dump(inputs, f, sort_keys=True, indent=4, separators=(',', ': '))

        self.add_preset(filename)

        return filename

    def load_active_preset(self):
        pass

    def _process_presets(self):
        pass

    def _default_browse_path(self):
        """
        Returns the current browse path for save/load preset
        If a preset is currently loaded it will use that specific path otherwise it will
        go to the last registered preset path
        :return: str, path to use as default browse location
        """

        current_index = self.presets.currentIndex()
        path = self.presets.itemData(current_index)
        if not path:
            paths = self.get_preset_paths()
            if paths:
                path = paths[-1]

        return path

    def _on_save_preset(self):
        """
        Save playblast template to a file
        """

        inputs = self.inputs_getter(as_preset=True)
        self.save_preset(inputs)


class SolsticePlayBlast(solstice_windows.Window, object):

    optionsChanged = Signal(dict)
    playblastStart = Signal(dict)
    playblastFinished = Signal(dict)
    viewerStart = Signal(dict)

    name = 'Solstice_PlayBlast'
    title = 'Solstice Tools - Playblast Tool'
    version = '1.0'
    docked = True

    def __init__(self, parent=None, **kwargs):

        self.playblast_widgets = list()
        self.config_dialog = None

        super(SolsticePlayBlast, self).__init__(parent=parent, **kwargs)

    def custom_ui(self):
        super(SolsticePlayBlast, self).custom_ui()

        self.set_logo('solstice_playblast_logo')

        self.setMinimumWidth(380)

        # ========================================================================================================

        self._build_configuration_dialog()

        # ========================================================================================================

        self.main_widget = solstice_accordion.AccordionWidget(parent=self)
        self.main_widget.rollout_style = solstice_accordion.AccordionStyle.MAYA
        self.main_layout.addWidget(self.main_widget)

        # ========================================================================================================

        self.preset_widget = PlayblastPreset(inputs_getter=self.get_inputs, parent=self)
        self.main_widget.add_item('Presets', self.preset_widget, collapsed=False)

        # ========================================================================================================

        self.main_widget.add_item('Preview', PlayblastPreview(options=self.get_outputs, validator=self.validate, parent=self), collapsed=False)

        # ========================================================================================================

        self.default_options = DefaultPlayblastOptions()
        self.playblast_widgets.append(self.default_options)

        # ========================================================================================================

        self.time_range = SolsticeTimeRange()
        self.cameras = SolsticeCameras()
        self.resolution = SolsticeResolution()
        self.codec = SolsticeCodec()
        self.options = BasePlayblastOptions()

        for widget in [self.time_range, self.cameras, self.resolution, self.codec, self.options]:
            widget.initialize()
            widget.optionsChanged.connect(self._on_update_settings)
            self.playblastFinished.connect(widget.on_playblast_finished)
            item = self.main_widget.add_item(widget.id, widget)
            self.playblast_widgets.append(widget)
            if item is not None:
                widget.labelChanged.connect(item.setTitle)

        # ========================================================================================================

        self.capture_btn = QPushButton('C A P T U R E')
        self.main_layout.addWidget(self.capture_btn)

        self.capture_btn.clicked.connect(self._on_capture)
        self.preset_widget.configOpened.connect(self.show_config)
        self.preset_widget.presetLoaded.connect(self.apply_inputs)
        self.apply_inputs(inputs=self._read_configuration())

    def cleanup(self):
        super(SolsticePlayBlast, self).cleanup()
        self._store_configuration()
        for widget in self.playblast_widgets:
            if hasattr(widget, 'uninitialize'):
                widget.uninitialize()

    def validate(self):
        errors = list()
        for widget in self.playblast_widgets:
            if hasattr(widget, 'validate'):
                widget_errors = widget.validate()
                if widget_errors:
                    errors.extend(widget_errors)

        if errors:
            message_title = '{} Validation Error(s)'.format(len(errors))
            message = '\n'.join(errors)
            QMessageBox.critical(self, message_title, message, QMessageBox.Ok)
            return False

        return True

    def get_inputs(self, as_preset=False):
        inputs = dict()
        config_widgets = self.playblast_widgets
        config_widgets.append(self.preset_widget)
        for widget in config_widgets:
            widget_inputs = widget.get_inputs(as_preset=as_preset)
            if not isinstance(widget_inputs, dict):
                sp.logger.debug('Widget inputs are not a valid dictionary "{0}" : "{1}"'.format(widget.id, widget_inputs))
                return
            if not widget_inputs:
                continue
            inputs[widget.id] = widget_inputs

        return inputs

    def apply_inputs(self, inputs):
        if not inputs:
            return

        widgets = self.playblast_widgets
        widgets.append(self.preset_widget)
        for widget in widgets:
            widget_inputs = inputs.get(widget.id, None)
            if not widget_inputs:
                contextlib
            widget.apply_inputs(widget_inputs)

    def get_outputs(self):
        outputs = dict()
        for widget in self.playblast_widgets:
            if hasattr(widget, 'get_outputs'):
                widget_outputs = widget.get_outputs()
                if not widget_outputs:
                    continue
                for key, value in widget_outputs.items():
                    if isinstance(value, dict) and key in outputs:
                        outputs[key].update(value)
                    else:
                        outputs[key] = value

        return outputs

    def show_config(self):
        """
        Shows advanced configuration dialog
        """

        geometry = self.geometry()
        self.config_dialog.move(QPoint(geometry.x() + 30, geometry.y()))
        self.config_dialog.show()

    def _read_configuration(self):
        inputs = dict()
        path = self.settings.config_file
        if not os.path.isfile(path) or os.stat(path).st_size == 0:
            return inputs

        for section in self.settings.sections():
            if section == self.name.lower():
                continue
            inputs[section] = dict()
            props = self.settings.items(section)
            for prop in props:
                inputs[section][str(prop[0])] = str(prop[1])

        return inputs

    def _store_configuration(self):
        inputs = self.get_inputs(as_preset=False)
        for widget_id, attrs_dict in inputs.items():
            if not self.settings.has_section(widget_id):
                self.settings.add_section(widget_id)
            for attr_name, attr_value in attrs_dict.items():
                self.settings.set(widget_id, attr_name, attr_value)
        self.settings.update()

    def _build_configuration_dialog(self):
        """
        Build configuration dialog to store configuration widgets in
        """

        self.config_dialog = QDialog(self)
        self.config_dialog.setWindowTitle('Solstice Playblast - Advanced Configuration')
        QVBoxLayout(self.config_dialog)

    def _on_update_settings(self):
        self.optionsChanged.emit(self.get_outputs)
        self.preset_widget.presets.setCurrentIndex(0)

    def _on_capture(self):
        valid = self.validate()
        if not valid:
            return

        options = self.get_outputs()
        filename = options.get('filename', None)

        self.playblastStart.emit(options)

        if filename is not None:
            print('Creating capture')

        options['filename'] = filename
        options['filename'] = capture_scene(options=options)

        self.playblastFinished.emit(filename)

        filename = options['filename']

        viewer = options.get('viewer', False)
        if viewer:
            if filename and os.path.exists(filename):
                self.viewerStart.emit(options)
                python.open_file(file_path=filename)
            else:
                raise RuntimeError('Cannot open playblast because file "{}" does not exists!'.format(filename))

        return filename


# ==================================================================================================================

def capture(**kwargs):
    """
    Creates a playblast in an independent panel
    :param kwargs:
    """

    filename = kwargs.get('filename', None)
    camera = kwargs.get('camera', 'persp')
    sound = kwargs.get('sound', None)
    width = kwargs.get('width', cmds.getAttr('defaultResolution.width'))
    height = kwargs.get('height', cmds.getAttr('defaultResolution.height'))
    format = kwargs.get('format', 'qt')
    compression = kwargs.get('compression', 'H.264')
    quality = kwargs.get('quality', 100)
    maintain_aspect_ratio = kwargs.get('maintain_aspect_ratio', True)
    frame = kwargs.get('frame', None)
    start_frame = kwargs.get('start_frame', cmds.playbackOptions(query=True, minTime=True))
    end_frame = kwargs.get('end_frame', cmds.playbackOptions(query=True, maxTime=True))
    complete_filename = kwargs.get('complete_filename', None)
    off_screen = kwargs.get('off_screen', False)
    isolate = kwargs.get('isolate', None)
    viewer = kwargs.get('viewer', None)
    show_ornaments = kwargs.get('show_ornaments', True)
    overwrite = kwargs.get('overwrite', False)
    frame_padding = kwargs.get('frame_padding', 4)
    raw_frame_numbers = kwargs.get('raw_frame_numbers', False)

    if not cmds.objExists(camera):
        raise RuntimeError('Camera does not exists!'.format(camera))

    if maintain_aspect_ratio:
        ratio = cmds.getAttr('defaultResolution.deviceAspectRatio')
        height = round(width / ratio)

    if start_frame is None:
        start_frame = cmds.playbackOptions(query=True, minTime=True)
    if end_frame is None:
        end_frame = cmds.playbackOptions(query=True, maxTime=True)

    if raw_frame_numbers and frame is None:
        frame = range(int(start_frame), int(end_frame) + 1)

    playblast_kwargs = dict()
    if complete_filename:
        playblast_kwargs['completeFilename'] = complete_filename
    if frame is not None:
        playblast_kwargs['frame'] = frame
    if sound is not None:
        playblast_kwargs['kwargs'] = sound

    if frame and raw_frame_numbers:
        check = frame if isinstance(frame, (list, tuple)) else [frame]
        if any(f < 0 for f in check):
            raise RuntimeError('Negative frames are not supported with raw frame numbers and explicit frame numbers')

    cmds.currentTime(cmds.currentTime(query=True))

    padding = 10
    with utils.create_independent_panel(width=width+padding, height=height+padding, off_screen=off_screen) as panel:
        cmds.setFocus(panel)
        with contextlib.nested(
            utils.disable_inview_messages(),
            utils.maintain_camera_on_panel(panel=panel, camera=camera),
            utils.isolated_nodes(nodes=isolate, panel=panel),
            utils.reset_time()
        ):

            output = cmds.playblast(
                compression=compression,
                format=format,
                percent=100,
                quality=quality,
                viewer=viewer,
                startTime=start_frame,
                endTime=end_frame,
                offScreen=off_screen,
                showOrnaments=show_ornaments,
                forceOverwrite=overwrite,
                filename=filename,
                widthHeight=[width, height],
                rawFrameNumbers=raw_frame_numbers,
                framePadding=frame_padding,
                **playblast_kwargs
            )

        return output


def capture_scene(options):
    """
    Capturing using scene settings
    :param options: dict, collection of output options
    :return: str, path to playblast file
    """

    filename = options.get('filename', '%TEMP%')
    sp.logger.info('Capturing to {}'.format(filename))
    options = options.copy()

    # Force viewer to False in call to capture because we have our own viewer opening call to allow a signal
    # to trigger between playblast and viewer
    options['viewer'] = False
    options.pop('panel', None)

    path = capture(**options)
    path = utils.fix_playblast_output_path(path)

    return path


def parse_current_scene():
    """
    Parse current Maya scene looking for settings related with play blasts
    :return: dict
    """

    time_control = mel.eval("$gPlayBackSlider = $gPlayBackSlider")

    return {
        'start_frame': cmds.playbackOptions(query=True, minTime=True),
        'end_frame': cmds.playbackOptions(query=True, maxTime=True),
        'width': cmds.getAttr('defaultResolution.width'),
        'height': cmds.getAttr('defaultResolution.height'),
        'compression': cmds.optionVar(query='playblastCompression'),
        'filename': (cmds.optionVar(query='playblastFile') if cmds.optionVar(query='playblastSaveToFile') else None),
        'format': cmds.optionVar(query='playblastFormat'),
        'off_scren': (True if cmds.optionVar(query='playblastOffscreen') else False),
        'show_ornaments': (True if cmds.optionVar(query='playblastShowOrnaments') else False),
        'quality': cmds.optionVar(query='playblastQuality'),
        'sound': cmds.timeControl(time_control, query=True, sound=True) or None
    }

# ==================================================================================================================


def run():
    reload(solstice_accordion)
    reload(solstice_label)
    reload(utils)
    reload(python)
    SolsticePlayBlast.run()
