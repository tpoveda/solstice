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
import maya.OpenMaya as OpenMayaV1
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaRender as OpenMayaRender
import maya.api.OpenMayaUI as OpenMayaUI

import solstice_pipeline as sp
from solstice_pipeline.solstice_gui import solstice_windows, solstice_label, solstice_buttons, solstice_accordion, solstice_sync_dialog, solstice_splitters
from solstice_pipeline.solstice_utils import solstice_maya_utils as utils
from solstice_pipeline.solstice_utils import solstice_python_utils as python
from solstice_pipeline.solstice_utils import solstice_qt_utils
from solstice_pipeline.resources import solstice_resource

# ========================================================================================================

CameraOptions = {
    "displayGateMask": False,
    "displayResolution": False,
    "displayFilmGate": False,
    "displayFieldChart": False,
    "displaySafeAction": False,
    "displaySafeTitle": False,
    "displayFilmPivot": False,
    "displayFilmOrigin": False,
    "overscan": 1.0,
    "depthOfField": False,
}

DisplayOptions = {
    "displayGradient": True,
    "background": (0.631, 0.631, 0.631),
    "backgroundTop": (0.535, 0.617, 0.702),
    "backgroundBottom": (0.052, 0.052, 0.052),
}

_DisplayOptionsRGB = set(["background", "backgroundTop", "backgroundBottom"])

ViewportOptions = {
    "rendererName": "vp2Renderer",
    "fogging": False,
    "fogMode": "linear",
    "fogDensity": 1,
    "fogStart": 1,
    "fogEnd": 1,
    "fogColor": (0, 0, 0, 0),
    "shadows": False,
    "displayTextures": True,
    "displayLights": "default",
    "useDefaultMaterial": False,
    "wireframeOnShaded": False,
    "displayAppearance": 'smoothShaded',
    "selectionHiliteDisplay": False,
    "headsUpDisplay": True,
    "imagePlane": True,
    "nurbsCurves": False,
    "nurbsSurfaces": False,
    "polymeshes": True,
    "subdivSurfaces": False,
    "planes": True,
    "cameras": False,
    "controlVertices": True,
    "lights": False,
    "grid": False,
    "hulls": True,
    "joints": False,
    "ikHandles": False,
    "deformers": False,
    "dynamics": False,
    "fluids": False,
    "hairSystems": False,
    "follicles": False,
    "nCloths": False,
    "nParticles": False,
    "nRigids": False,
    "dynamicConstraints": False,
    "locators": False,
    "manipulators": False,
    "dimensions": False,
    "handles": False,
    "pivots": False,
    "textures": False,
    "strokes": False
}

Viewport2Options = {
    "consolidateWorld": True,
    "enableTextureMaxRes": False,
    "bumpBakeResolution": 64,
    "colorBakeResolution": 64,
    "floatingPointRTEnable": True,
    "floatingPointRTFormat": 1,
    "gammaCorrectionEnable": False,
    "gammaValue": 2.2,
    "lineAAEnable": False,
    "maxHardwareLights": 8,
    "motionBlurEnable": False,
    "motionBlurSampleCount": 8,
    "motionBlurShutterOpenFraction": 0.2,
    "motionBlurType": 0,
    "multiSampleCount": 8,
    "multiSampleEnable": False,
    "singleSidedLighting": False,
    "ssaoEnable": False,
    "ssaoAmount": 1.0,
    "ssaoFilterRadius": 16,
    "ssaoRadius": 16,
    "ssaoSamples": 16,
    "textureMaxResolution": 4096,
    "threadDGEvaluation": False,
    "transparencyAlgorithm": 1,
    "transparencyQuality": 0.33,
    "useMaximumHardwareLights": True,
    "vertexAnimationCache": 0
}
if mel.eval('getApplicationVersionAsFloat') > 2015:
    ViewportOptions.update({
        "motionTrails": False
    })
    Viewport2Options.update({
        "hwFogAlpha": 1.0,
        "hwFogFalloff": 0,
        "hwFogDensity": 0.1,
        "hwFogEnable": False,
        "holdOutDetailMode": 1,
        "hwFogEnd": 100.0,
        "holdOutMode": True,
        "hwFogColorR": 0.5,
        "hwFogColorG": 0.5,
        "hwFogColorB": 0.5,
        "hwFogStart": 0.0,
    })

# ========================================================================================================


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
        current_frame = OpenMayaV1.MEventMessage.addEventCallback('timeChanged', callback)
        time_range = OpenMayaV1.MEventMessage.addEventCallback('playbackRangeChanged', callback)
        self._event_callbacks.append(current_frame)
        self._event_callbacks.append(time_range)

    def _remove_callbacks(self):
        for callback in self._event_callbacks:
            try:
                OpenMayaV1.MEventMessage.removeCallback(callback)
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
        cmds.optionVar(sv=['solstice_playblast_camera', camera])
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


class SolsticeMaskObject(object):

    mask_plugin = 'solstice_playblast.py'
    mask_node = 'SolsticeMask'
    mask_transform = 'solsticemask'
    mask_shape = 'solsticemask_shape'

    def __init__(self):
        super(SolsticeMaskObject, self).__init__()

    @classmethod
    def create_mask(cls):
        if not cmds.pluginInfo('solstice_playblast.py', query=True, loaded=True):
            try:
                cmds.loadPlugin(cls.mask_plugin)
            except Exception:
                sp.logger.error('Failed to load SolsticeMask plugin!')
                return

        if not cls.get_mask():
            transform_node = cmds.createNode('transform', name=cls.mask_transform)
            cmds.createNode(cls.mask_node, name=cls.mask_shape, parent=transform_node)

        cls.refresh_mask()

    @classmethod
    def get_mask(cls):
        if cmds.pluginInfo(cls.mask_plugin, query=True, loaded=True):
            nodes = cmds.ls(type=cls.mask_node)
            if len(nodes) > 0:
                return nodes[0]

        return None

    @classmethod
    def delete_mask(cls):
        mask = cls.get_mask()
        if mask:
            transform = cmds.listRelatives(mask, fullPath=True, parent=True)
            if transform:
                cmds.delete(transform)
            else:
                cmds.delete(mask)

    @classmethod
    def get_camera_name(cls):
        if cmds.optionVar(exists='solstice_playblast_camera'):
            return cmds.optionVar(query='solstice_playblast_camera')
        else:
            return ''

    @classmethod
    def get_label_text(cls):
        if cmds.optionVar(exists='solstice_mask_'):
            pass

    @classmethod
    def refresh_mask(cls):
        mask = cls.get_mask()
        if not mask:
            return

        cmds.setAttr('{}.camera'.format(mask), cls.get_camera_name(), type='string')


class SolsticeMaskWidget(SolsticePlayblastWidget, object):

    id = 'Mask'
    label = 'Mask'

    def __init__(self, parent=None):
        super(SolsticeMaskWidget, self).__init__(parent=parent)

    def custom_ui(self):
        super(SolsticeMaskWidget, self).custom_ui()

        self.enable_mask_cbx = QCheckBox('Enable')
        self.main_layout.addWidget(self.enable_mask_cbx)
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        labels_layout = QVBoxLayout()
        labels_group = QGroupBox('Labels')
        labels_group.setLayout(labels_layout)
        self.main_layout.addWidget(labels_group)

        grid_layout = QGridLayout()
        labels_layout.addLayout(grid_layout)

        top_left_lbl = QLabel('Top Left: ')
        top_center_lbl = QLabel('Top Center: ')
        top_right_lbl = QLabel('Top Right: ')
        bottom_left_lbl = QLabel('Bottom Left: ')
        bottom_center_lbl = QLabel('Bottom Center: ')
        bottom_right_lbl = QLabel('Bottom Right: ')
        font_lbl = QLabel('Font: ')
        color_lbl = QLabel('Color: ')
        alpha_lbl = QLabel('Transparency: ')
        scale_lbl = QLabel('Scale: ')

        self.top_left_line = QLineEdit()
        self.top_center_line = QLineEdit()
        self.top_right_line = QLineEdit()
        self.bottom_left_line = QLineEdit()
        self.bottom_center_line = QLineEdit()
        self.bottom_right_line = QLineEdit()
        self.font_line = QLineEdit()
        self.font_line.setReadOnly(True)
        self.font_btn = QPushButton('...')
        self.color_btn = solstice_buttons.ColorButton(colorR=1, colorG=1, colorB=1)
        self.alpha_btn = solstice_buttons.ColorButton(colorR=1, colorG=1, colorB=1)
        self.scale_spn = QDoubleSpinBox()
        self.scale_spn.setRange(0.1, 2.0)
        self.scale_spn.setValue(1.0)
        self.scale_spn.setSingleStep(0.01)
        self.scale_spn.setDecimals(2)
        self.scale_spn.setMaximumWidth(80)

        grid_layout.addWidget(top_left_lbl, 0, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(top_center_lbl, 1, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(top_right_lbl, 2, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(bottom_left_lbl, 3, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(bottom_center_lbl, 4, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(bottom_right_lbl, 5, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(font_lbl, 6, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(color_lbl, 7, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(alpha_lbl, 8, 0, alignment=Qt.AlignLeft)
        grid_layout.addWidget(scale_lbl, 9, 0, alignment=Qt.AlignLeft)

        grid_layout.addWidget(self.top_left_line, 0, 1)
        grid_layout.addWidget(self.top_center_line, 1, 1)
        grid_layout.addWidget(self.top_right_line, 2, 1)
        grid_layout.addWidget(self.bottom_left_line, 3, 1)
        grid_layout.addWidget(self.bottom_center_line, 4, 1)
        grid_layout.addWidget(self.bottom_right_line, 5, 1)
        grid_layout.addWidget(self.font_line, 6, 1)
        grid_layout.addWidget(self.font_btn, 6, 2)
        grid_layout.addWidget(self.font_btn, 6, 2)
        grid_layout.addWidget(self.color_btn, 7, 1)
        grid_layout.addWidget(self.alpha_btn, 8, 1)
        grid_layout.addWidget(self.scale_spn, 9, 1)

        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # ========================================================================

        borders_layout = QVBoxLayout()
        borders_layout.setAlignment(Qt.AlignLeft)
        borders_group = QGroupBox('Borders')
        borders_group.setLayout(borders_layout)
        self.main_layout.addWidget(borders_group)

        cbx_layout = QHBoxLayout()
        grid_layout_2 = QGridLayout()
        borders_layout.addLayout(cbx_layout)
        borders_layout.addLayout(grid_layout_2)

        border_color_lbl = QLabel('Color: ')
        border_alpha_lbl = QLabel('Transparency: ')
        border_scale_lbl = QLabel('Scale: ')

        self.top_cbx = QCheckBox('Top')
        self.top_cbx.setChecked(True)
        self.bottom_cbx = QCheckBox('Bottom')
        self.bottom_cbx.setChecked(True)
        cbx_layout.addWidget(self.top_cbx)
        cbx_layout.addWidget(self.bottom_cbx)

        self.border_color_btn = solstice_buttons.ColorButton(colorR=0, colorG=0, colorB=0)
        self.border_color_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.border_alpha_btn = solstice_buttons.ColorButton(colorR=1, colorG=1, colorB=1)
        self.border_scale_spn = QDoubleSpinBox()
        self.border_scale_spn.setRange(0.5, 2.0)
        self.border_scale_spn.setValue(1.0)
        self.border_scale_spn.setSingleStep(0.01)
        self.border_scale_spn.setDecimals(2)
        self.border_scale_spn.setMaximumWidth(80)

        grid_layout_2.addWidget(border_color_lbl, 0, 0, alignment=Qt.AlignLeft)
        grid_layout_2.addWidget(border_alpha_lbl, 1, 0, alignment=Qt.AlignLeft)
        grid_layout_2.addWidget(border_scale_lbl, 2, 0, alignment=Qt.AlignLeft)

        grid_layout_2.addWidget(self.border_color_btn, 0, 1)
        grid_layout_2.addWidget(self.border_alpha_btn, 1, 1)
        grid_layout_2.addWidget(self.border_scale_spn, 2, 1)

        # ========================================================================

        counter_layout = QVBoxLayout()
        counter_layout.setAlignment(Qt.AlignLeft)
        counter_group = QGroupBox('Counter')
        counter_group.setLayout(counter_layout)
        self.main_layout.addWidget(counter_group)

        self.enable_cbx = QCheckBox('Enable: ')
        grid_layout_3 = QGridLayout()
        counter_layout.addWidget(self.enable_cbx)
        counter_layout.addLayout(grid_layout_3)

        align_lbl = QLabel('Alignment: ')
        padding_lbl = QLabel('Padding: ')

        self.align_combo = QComboBox()
        self.align_combo.addItem('Top-Left')
        self.align_combo.addItem('Top-Right')
        self.align_combo.addItem('Bottom-Left')
        self.align_combo.addItem('Bottom-Right')
        self.padding_spn = QSpinBox()
        self.padding_spn.setRange(1, 6)
        self.padding_spn.setValue(1)
        self.padding_spn.setSingleStep(1)
        self.padding_spn.setMaximumWidth(80)

        grid_layout_3.addWidget(align_lbl, 0, 0, alignment=Qt.AlignLeft)
        grid_layout_3.addWidget(padding_lbl, 1, 0, alignment=Qt.AlignLeft)

        grid_layout_3.addWidget(self.align_combo, 0, 1)
        grid_layout_3.addWidget(self.padding_spn, 1, 1)

    def apply_inputs(self, attr_dict):
        pass

    def get_outputs(self):
        return {}


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

        open_playblasts_folder_icon = solstice_resource.icon('movies_folder')
        self.open_playblasts_folder_btn = QPushButton()
        self.open_playblasts_folder_btn.setIcon(open_playblasts_folder_icon)
        self.open_playblasts_folder_btn.setFixedWidth(25)
        self.open_playblasts_folder_btn.setFixedHeight(25)
        self.open_playblasts_folder_btn.setIconSize(QSize(25, 25))
        self.open_playblasts_folder_btn.setToolTip('Open Playblasts Folder')
        self.open_playblasts_folder_btn.setStatusTip('Open Playblasts Folder')
        self.open_playblasts_folder_btn.setParent(self.preview)
        self.open_playblasts_folder_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        self.open_playblasts_folder_btn.move(5, 5)

        sync_icon = solstice_resource.icon('sync')
        self.sync_preview_btn = QPushButton()
        self.sync_preview_btn.setIcon(sync_icon)
        self.sync_preview_btn.setFixedWidth(25)
        self.sync_preview_btn.setFixedHeight(25)
        self.sync_preview_btn.setIconSize(QSize(25, 25))
        self.sync_preview_btn.setToolTip('Sync Preview')
        self.sync_preview_btn.setStatusTip('Sync Preview')
        self.sync_preview_btn.setParent(self.preview)
        self.sync_preview_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 0px solid rgba(255,255,255,0);")
        self.sync_preview_btn.move(32, 5)

        # self.preview.clicked.connect(self.refresh)
        self.sync_preview_btn.clicked.connect(self.refresh)

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
        self.presets.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

        vertical_separator = QFrame()
        vertical_separator.setFrameShape(QFrame.VLine)
        vertical_separator.setFrameShadow(QFrame.Sunken)

        open_templates_folder_icon = solstice_resource.icon('overview')
        self.open_templates_folder_btn = QPushButton()
        self.open_templates_folder_btn.setIcon(open_templates_folder_icon)
        self.open_templates_folder_btn.setFixedWidth(30)
        self.open_templates_folder_btn.setToolTip('Open Templates Folder')
        self.open_templates_folder_btn.setStatusTip('Open Templates Folder')

        for widget in [self.presets, self.save, self.load, self.preset_config, vertical_separator, self.open_templates_folder_btn]:
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
        """
        Add the filename to the presets list
        :param filename: str
        """

        filename = os.path.normpath(filename)
        if not os.path.exists(filename):
            sp.logger.warning('Preset file does not exists: "{}"'.format(filename))
            return

        label = os.path.splitext(os.path.basename(filename))[0]
        item_count = self.presets.count()

        paths = [self.presets.itemData(i) for i in range(item_count)]
        if filename in paths:
            sp.logger.info('Preset is already in the presets list: "{}"'.format(filename))
            item_index = paths.index(filename)
        else:
            self.presets.addItem(label, userData=filename)
            item_index = item_count

        self.presets.blockSignals(True)
        self.presets.setCurrentIndex(item_index)
        self.presets.blockSignals(False)

        return item_index

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
        """
        Loads the active preset
        :return: dict, preset inputs
        """

        current_index = self.presets.currentIndex()
        filename = self.presets.itemData(current_index)
        if not filename:
            return {}

        preset = python.load_json(filename)
        self.presetLoaded.emit(preset)

        self.presets.blockSignals(True)
        self.presets.setCurrentIndex(current_index)
        self.presets.blockSignals(False)

        return preset

    def _process_presets(self):
        """
        Adds all preset files from preset paths
        """

        for preset_file in self.discover_presets():
            self.add_preset(preset_file)

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

    def __init__(self):

        self.playblast_widgets = list()
        self.config_dialog = None

        super(SolsticePlayBlast, self).__init__()

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
        self.mask = SolsticeMaskWidget()

        for widget in [self.time_range, self.cameras, self.resolution, self.codec, self.options, self.mask]:
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
                continue
            if widget_inputs:
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
    camera_options = kwargs.get('camera_options', None)
    display_options = kwargs.get('display_options', None)
    viewport_options = kwargs.get('viewport_options', None)
    viewport2_options = kwargs.get('viewport2_options', None)

    camera = camera or 'persp'
    if not cmds.objExists(camera):
        raise RuntimeError('Camera does not exists!'.format(camera))

    width = width or cmds.getAttr('defaultResolution.width')
    height = height or cmds.getAttr('defaultResolution.height')
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
        playblast_kwargs['sound'] = sound

    if frame and raw_frame_numbers:
        check = frame if isinstance(frame, (list, tuple)) else [frame]
        if any(f < 0 for f in check):
            raise RuntimeError('Negative frames are not supported with raw frame numbers and explicit frame numbers')

    cmds.currentTime(cmds.currentTime(query=True))

    padding = 10
    with utils.create_independent_panel(width=width+padding, height=height+padding, off_screen=off_screen) as panel:
        cmds.setFocus(panel)
        with contextlib.nested(
            _applied_viewport_options(viewport_options, panel),
            _applied_camera_options(camera_options, panel),
            _applied_display_options(display_options),
            _applied_viewport2_options(viewport2_options),
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


def snap(*args, **kwargs):
    """
    Single frame playblast in an independent panel
    """

    frame = kwargs.pop('frame', cmds.currentTime(query=True))
    kwargs['start_frame'] = frame
    kwargs['end_frame'] = frame
    kwargs['frame'] = frame
    if not isinstance(frame, (int, float)):
        raise TypeError('Frame must be a single frame (integer or float). For sequences use capture function.')

    format = kwargs.pop('format', 'image')
    compression = kwargs.get('compression', 'png')
    viewer = kwargs.pop('viewer', False)
    raw_frame_numbers = kwargs.pop('raw_frame_numbers', True)
    kwargs['compression'] = compression
    kwargs['format'] = format
    kwargs['viewer'] = viewer
    kwargs['raw_frame_numbers'] = raw_frame_numbers

    clipboard = kwargs.get('clipboard', False)

    output = capture(*args, **kwargs)

    def replace(m):
        return str(int(frame)).zfill(len(m.group()))

    if clipboard:
        solstice_qt_utils.image_to_clipboard(output)

    return output


def parse_view(panel):
    """
    Parse the scene, panel and camera looking for their current settings
    :param panel: str
    """

    camera = cmds.modelPanel(panel, query=True, camera=True)
    display_options = dict()
    camera_options = dict()
    viewport_options = dict()
    viewport2_options = dict()

    for key in DisplayOptions:
        if key in _DisplayOptionsRGB:
            display_options[key] = cmds.displayRGBColor(key, query=True)
        else:
            display_options[key] = cmds.displayPref(query=True, **{key: True})
    for key in CameraOptions:
        camera_options[key] = cmds.getAttr('{0}.{1}'.format(camera, key))
    widgets = cmds.pluginDisplayFilter(query=True, listFilters=True)
    for widget in widgets:
        widget = str(widget)
        state = cmds.modelEditor(panel, query=True, queryPluginObjects=widget)
        viewport_options[widget] = state
    for key in ViewportOptions:
        viewport_options[key] = cmds.modelEditor(panel ,query=True, **{key: True})
    for key in Viewport2Options.keys():
        attr = 'hardwareRenderingGlobals.{}'.format(key)
        try:
            viewport2_options[key] = cmds.getAttr(attr)
        except ValueError:
            continue

    return {
        "camera": camera,
        "display_options": display_options,
        "camera_options": camera_options,
        "viewport_options": viewport_options,
        "viewport2_options": viewport2_options
    }


def parse_active_view():
    """
    Parses the current settings from the active view
    :return: str
    """

    panel = utils.get_active_panel()
    return parse_view(panel)


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


def apply_view(panel, **options):
    """
    Apply options to panel
    :param panel: str
    :param options: dict
    """

    camera = cmds.modelPanel(query=True, camera=True)

    display_options = options.get('display_options', {})
    for key, value in display_options.items():
        if key in _DisplayOptionsRGB:
            cmds.displayRGBColor(key, *value)
        else:
            cmds.displayPref(**{key: value})
    camera_options = options.get('camera_options', {})
    for key, value in camera_options.items():
        cmds.setAttr('{0}.{1}'.format(camera, key), value)
    viewport_options = options.get('viewport_options', {})
    for key, value in viewport_options.items():
        cmds.modelEditor(panel, edit=True, **{key: value})
    viewport2_options = options.get('viewport2_options', {})
    for key, value in viewport2_options.items():
        attr = 'hardwareRenderingGlobals.{}'.format(key)
        cmds.setAttr(attr, value)


def apply_scene(**options):
    """
    Apply options from scene
    :param options: dict
    """

    if "start_frame" in options:
        cmds.playbackOptions(minTime=options["start_frame"])

    if "end_frame" in options:
        cmds.playbackOptions(maxTime=options["end_frame"])

    if "width" in options:
        cmds.setAttr("defaultResolution.width", options["width"])

    if "height" in options:
        cmds.setAttr("defaultResolution.height", options["height"])

    if "compression" in options:
        cmds.optionVar(
            stringValue=["playblastCompression", options["compression"]])

    if "filename" in options:
        cmds.optionVar(
            stringValue=["playblastFile", options["filename"]])

    if "format" in options:
        cmds.optionVar(
            stringValue=["playblastFormat", options["format"]])

    if "off_screen" in options:
        cmds.optionVar(
            intValue=["playblastFormat", options["off_screen"]])

    if "show_ornaments" in options:
        cmds.optionVar(
            intValue=["show_ornaments", options["show_ornaments"]])

    if "quality" in options:
        cmds.optionVar(
            floatValue=["playblastQuality", options["quality"]])


@contextlib.contextmanager
def _applied_camera_options(options, panel):
    """
    Context manager for applying options to camera
    :param options: dict
    :param panel: str
    """

    camera = cmds.modelPanel(panel, query=True, camera=True)
    options = dict(CameraOptions, **(options or {}))
    old_options = dict()

    for option in options.copy():
        try:
            old_options[option] = cmds.getAttr(camera + '.' + option)
        except Exception as e:
            sys.stderr.write('Could not get camera attribute for capture: "{}"'.format(option))

    for option, value in options.items():
        cmds.setAttr(camera + '.' + option, value)

    try:
        yield
    finally:
        if old_options:
            for option, value in old_options.items():
                cmds.setAttr(camera + '.' + option, value)


@contextlib.contextmanager
def _applied_display_options(options):
    """
    Context manager for setting background color display options
    :param options: dict
    """

    options = dict(DisplayOptions, **(options or {}))
    colors = ['background', 'backgroundTop', 'backgroundBottom']
    preferences = ['displayGradient']
    original = dict()

    for color in colors:
        original[color] = cmds.displayRGBColor(color, query=True) or []
    for preference in preferences:
        original[preference] = cmds.displayPref(query=True, **{preference: True})
    for color in colors:
        value = options[color]
        cmds.displayRGBColor(color, *value)
    for preference in preferences:
        value = options[preference]
        cmds.displayPref(**{preference: value})

    try:
        yield
    finally:
        for color in colors:
            cmds.displayRGBColor(color, *original[color])
        for preference in preferences:
            cmds.displayPref(**{preference: original[preference]})


@contextlib.contextmanager
def _applied_viewport_options(options, panel):
    """
    Context manager for applying options to panel
    :param options: dict
    :param panel: str
    """

    options = dict(ViewportOptions, **(options or {}))
    playblast_widgets = cmds.pluginDisplayFilter(query=True, listFilters=True)
    widget_options = dict()
    for widget in playblast_widgets:
        if widget in options:
            widget_options[widget] = options.pop(widget)

    cmds.modelEditor(panel, edit=True, **options)

    for widget, state in widget_options.items():
        cmds.modelEditor(panel, edit=True, pluginObjects=(widget, state))

    yield


@contextlib.contextmanager
def _applied_viewport2_options(options):
    """
    Context manager for setting viewport 2.0 options
    :param options: dict
    """

    options = dict(Viewport2Options, **(options or {}))
    original = dict()

    for option in options.copy():
        try:
            original[option] = cmds.getAttr('hardwareRenderingGlobals.' + option)
        except ValueError:
            options.pop(option)
    for option, value in options.items():
        cmds.setAttr('hardwareRenderingGlobals.' + option, value)

    try:
        yield
    finally:
        for option, value in original.items():
            cmds.setAttr('hardwareRenderingGlobals.' + option, value)


@contextlib.contextmanager
def _applied_view(panel, **options):
    """
    Apply options to panel
    :param panel: str
    :param options: dict
    """

    original = parse_view(panel)
    apply_view(panel, **options)

    try:
        yield
    finally:
        apply_view(panel, **original)

# ==================================================================================================================

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class MaskTextAlignment(object):
    TopLeft = ['topLeftText', 'tlt']
    TopCenter = ['topCenterText', 'tct']
    TopRight = ['topRightText', 'trt']
    BottomLeft = ['bottomLeftText', 'blt']
    BottomCenter = ['bottomCenterText', 'bct']
    BottomRight = ['bottomRightText', 'brt']


class SolsticeMaskLocator(OpenMayaUI.MPxLocatorNode, object):
    _NAME_ = 'SolsticeMask'
    _ID_ = OpenMaya.MTypeId(0x1111B159)
    _DRAW_DB_CLASSIFICATION_ = 'drawdb/geometry/SolsticeMask'
    _DRAW_REGISTRANT_ID_ = 'SolsticeMaskNode'
    _TEXT_ATTRS_ = [
        MaskTextAlignment.TopLeft,
        MaskTextAlignment.TopCenter,
        MaskTextAlignment.TopRight,
        MaskTextAlignment.BottomLeft,
        MaskTextAlignment.BottomCenter,
        MaskTextAlignment.BottomRight
    ]

    def __init__(self):
        super(SolsticeMaskLocator, self).__init__()

    @classmethod
    def creator(cls):
        return SolsticeMaskLocator()

    @classmethod
    def initialize(cls):
        t_attr = OpenMaya.MFnTypedAttribute()
        str_data = OpenMaya.MFnStringData()
        n_attr = OpenMaya.MFnNumericAttribute()

        test_attr = OpenMaya.MFnTypedAttribute()
        str_test = OpenMaya.MFnStringData()
        obj = str_test.create('')
        camera_name = t_attr.create('camera', 'cam', OpenMaya.MFnData.kString, obj)
        t_attr.writable = True
        t_attr.storable = True
        t_attr.keyable = False
        SolsticeMaskLocator.addAttribute(camera_name)

        counter_position = n_attr.create('counterPosition', 'cp', OpenMaya.MFnNumericData.kShort, 6)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0)
        n_attr.setMax(6)
        SolsticeMaskLocator.addAttribute(counter_position)

        counter_padding = n_attr.create('counterPadding', 'cpd', OpenMaya.MFnNumericData.kShort, 4)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(1)
        n_attr.setMax(6)
        SolsticeMaskLocator.addAttribute(counter_padding)

        for i in range(len(cls._TEXT_ATTRS_)):
            obj = str_data.create('Position {}'.format(str(i / 2 + 1).zfill(2)))
            position = t_attr.create(cls._TEXT_ATTRS_[i][0], cls._TEXT_ATTRS_[i][1], OpenMaya.MFnData.kString, obj)
            t_attr.writable = True
            t_attr.storable = True
            t_attr.keyable = True
            SolsticeMaskLocator.addAttribute(position)

        text_padding = n_attr.create('textPadding', 'tp', OpenMaya.MFnNumericData.kShort, 10)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0)
        n_attr.setMax(50)
        SolsticeMaskLocator.addAttribute(text_padding)

        font_name = t_attr.create('fontName', 'ft', OpenMaya.MFnData.kString, str_data.create('Consolas'))
        t_attr.writable = True
        t_attr.storable = True
        t_attr.keyable = True
        SolsticeMaskLocator.addAttribute(font_name)

        font_color = n_attr.createColor("fontColor", "fc")
        n_attr.default = (1.0, 1.0, 1.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        SolsticeMaskLocator.addAttribute(font_color)

        font_alpha = n_attr.create("fontAlpha", "fa", OpenMaya.MFnNumericData.kFloat, 1.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0.0)
        n_attr.setMax(1.0)
        SolsticeMaskLocator.addAttribute(font_alpha)

        font_scale = n_attr.create("fontScale", "fs", OpenMaya.MFnNumericData.kFloat, 1.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0.1)
        n_attr.setMax(2.0)
        SolsticeMaskLocator.addAttribute(font_scale)

        top_border = n_attr.create("topBorder", "tbd", OpenMaya.MFnNumericData.kBoolean, True)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        SolsticeMaskLocator.addAttribute(top_border)

        bottom_border = n_attr.create("bottomBorder", "bbd", OpenMaya.MFnNumericData.kBoolean, True)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        SolsticeMaskLocator.addAttribute(bottom_border)

        border_color = n_attr.createColor("borderColor", "bc")
        n_attr.default = (0.0, 0.0, 0.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        SolsticeMaskLocator.addAttribute(border_color)

        border_alpha = n_attr.create("borderAlpha", "ba", OpenMaya.MFnNumericData.kFloat, 1.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0.0)
        n_attr.setMax(1.0)
        SolsticeMaskLocator.addAttribute(border_alpha)

        border_scale = n_attr.create("borderScale", "bs", OpenMaya.MFnNumericData.kFloat, 1.0)
        n_attr.writable = True
        n_attr.storable = True
        n_attr.keyable = True
        n_attr.setMin(0.5)
        n_attr.setMax(2.0)
        SolsticeMaskLocator.addAttribute(border_scale)


class SolsticeMaskData(OpenMaya.MUserData, object):
    def __init__(self):
        super(SolsticeMaskData, self).__init__(False)


class SolsticeMaskDrawOverride(OpenMayaRender.MPxDrawOverride, object):
    _NAME_ = 'SolsticeMask_draw_override'

    def __init__(self, obj):
        super(SolsticeMaskDrawOverride, self).__init__(obj, SolsticeMaskDrawOverride.draw)

    @staticmethod
    def creator(obj):
        return SolsticeMaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return

    def supportedDrawAPIs(self):
        return OpenMayaRender.MRenderer.kAllDevices

    def isBounded(self, obj_path, camera_path):
        return False

    def boundingBox(self, obj_path, camera_path):
        return OpenMaya.MBoundingBox()

    def hasUIDrawables(self):
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, SolsticeMaskData):
            data = SolsticeMaskData()

        dag_node_fn = OpenMaya.MFnDagNode(obj_path)
        data.camera_name = dag_node_fn.findPlug('camera', False).asString()
        data.text_fields = list()
        for i in range(len(SolsticeMaskLocator._TEXT_ATTRS_)):
            data.text_fields.append(dag_node_fn.findPlug(SolsticeMaskLocator._TEXT_ATTRS_[i][0], False).asString())
        counter_padding = dag_node_fn.findPlug('counterPadding', False).asInt()
        if counter_padding < 1:
            counter_padding = 1
        elif counter_padding > 6:
            counter_padding = 6
        current_time = int(cmds.currentTime(query=True))
        counter_position = dag_node_fn.findPlug('counterPosition', False).asInt()
        if counter_position > 0 and counter_position <= len(SolsticeMaskLocator._TEXT_ATTRS_):
            data.text_fields[counter_position-1] = '{}'.format(str(current_time).zfill(counter_padding))
        data.text_padding = dag_node_fn.findPlug('textPadding', False).asInt()
        data.font_name = dag_node_fn.findPlug('fontName', False).asString()
        r = dag_node_fn.findPlug('fontColorR', False).asFloat()
        g = dag_node_fn.findPlug('fontColorG', False).asFloat()
        b = dag_node_fn.findPlug('fontColorB', False).asFloat()
        a = dag_node_fn.findPlug('fontAlpha', False).asFloat()
        data.font_color = OpenMaya.MColor((r, g, b, a))
        data.font_scale = dag_node_fn.findPlug('fontScale', False).asFloat()
        br = dag_node_fn.findPlug('borderColorR', False).asFloat()
        bg = dag_node_fn.findPlug('borderColorG', False).asFloat()
        bb = dag_node_fn.findPlug('borderColorB', False).asFloat()
        ba = dag_node_fn.findPlug('borderAlpha', False).asFloat()
        data.border_color = OpenMaya.MColor((br, bg, bb , ba))
        data.border_scale = dag_node_fn.findPlug('borderScale', False).asFloat()
        data.top_border = dag_node_fn.findPlug('topBorder', False).asBool()
        data.bottom_border = dag_node_fn.findPlug('bottomBorder', False).asBool()

        return data

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, SolsticeMaskData):
            return

        icon_names = draw_manager.getIconNames()

        draw_manager.icon(OpenMaya.MPoint(50, 50), icon_names[5], 1.0)

        camera_path = frame_context.getCurrentCameraPath()
        camera = OpenMaya.MFnCamera(camera_path)
        if data.camera_name and self.camera_exists(data.camera_name) and not self.is_camera_match(camera_path, data.camera_name):
            return

        camera_aspect_ratio = camera.aspectRatio()
        device_aspect_ratio = cmds.getAttr('defaultResolution.deviceAspectRatio')
        vp_x, vp_y, vp_width, vp_height = frame_context.getViewportDimensions()
        vp_half_width = vp_width * 0.5
        vp_half_height = vp_height * 0.5
        vp_aspect_ratio = vp_width / float(vp_height)

        scale = 1.0

        if camera.filmFit == OpenMaya.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / camera.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == OpenMaya.MFnCamera.kVerticalFilmFit:
            mask_height = vp_height / camera.overscan
            mask_width = mask_height * device_aspect_ratio
        elif camera.filmFit == OpenMaya.MFnCamera.kFillFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio
            mask_width = vp_width / camera.overscan * scale
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == OpenMaya.MFnCamera.kOverscanFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_height = vp_height / camera.overscan / scale
            mask_width = mask_height * device_aspect_ratio
        else:
            OpenMaya.MGlobal.displayError('SolsticeShotMask: Unknown Film Fit value')
            return

        mask_half_width = mask_width * 0.5
        mask_x = vp_half_width - mask_half_width
        mask_half_height = 0.5 * mask_height
        mask_bottom_y = vp_half_height - mask_half_height
        mask_top_y = vp_half_height + mask_half_height
        border_height = int(0.05 * mask_height * data.border_scale)
        background_size = (int(mask_width), border_height)

        draw_manager.beginDrawable()
        draw_manager.setFontName(data.font_name)
        draw_manager.setFontSize(int((border_height - border_height * 0.15) * data.font_scale))
        draw_manager.setColor(data.font_color)

        print(data.border_color)

        if data.top_border:
            self.draw_border(draw_manager, OpenMaya.MPoint(mask_x, mask_top_y - border_height), background_size, data.border_color)
        if data.bottom_border:
            self.draw_border(draw_manager, OpenMaya.MPoint(mask_x, mask_bottom_y), background_size, data.border_color)

        self.draw_text(draw_manager, OpenMaya.MPoint(mask_x + data.text_padding, mask_top_y - border_height), data.text_fields[0], OpenMayaRender.MUIDrawManager.kLeft, background_size)
        self.draw_text(draw_manager, OpenMaya.MPoint(vp_half_width, mask_top_y - border_height), data.text_fields[1], OpenMayaRender.MUIDrawManager.kCenter, background_size)
        self.draw_text(draw_manager, OpenMaya.MPoint(mask_x + mask_width - data.text_padding, mask_top_y - border_height), data.text_fields[2], OpenMayaRender.MUIDrawManager.kRight, background_size)
        self.draw_text(draw_manager, OpenMaya.MPoint(mask_x + data.text_padding, mask_bottom_y), data.text_fields[3], OpenMayaRender.MUIDrawManager.kLeft, background_size)
        self.draw_text(draw_manager, OpenMaya.MPoint(vp_half_width, mask_bottom_y), data.text_fields[4], OpenMayaRender.MUIDrawManager.kCenter, background_size)
        self.draw_text(draw_manager, OpenMaya.MPoint(mask_x + mask_width - data.text_padding, mask_bottom_y), data.text_fields[5], OpenMayaRender.MUIDrawManager.kRight, background_size)

        draw_manager.endDrawable()

    def draw_border(self, draw_manager, position, background_size, color):
        draw_manager.text2d(position, ' ', alignment=OpenMayaRender.MUIDrawManager.kLeft, backgroundSize=background_size, backgroundColor=color)

    def draw_text(self, draw_manager, position, text, alignment, background_size):
        if len(text) > 0:
            draw_manager.text2d(position, text, alignment=alignment, backgroundSize=background_size, backgroundColor=OpenMaya.MColor((0.0, 0.0, 0.0, 0.0)))

    def camera_exists(self, name):
        return name in cmds.listCameras()

    def is_camera_match(self, camera_path, name):
        path_name = camera_path.fullPathName()
        split_path_name = path_name.split('|')
        if len(split_path_name) >= 1:
            if split_path_name[-1] == name:
                return True
        if len(split_path_name) >= 2:
            if split_path_name[-2] == name:
                return True

        return False


def initializePlugin(obj):
    plugin_fn = OpenMaya.MFnPlugin(obj, 'Solstice Short Film', '1.0', 'Any')
    try:
        plugin_fn.registerNode(
            SolsticeMaskLocator._NAME_,
            SolsticeMaskLocator._ID_,
            SolsticeMaskLocator.creator,
            SolsticeMaskLocator.initialize,
            OpenMaya.MPxNode.kLocatorNode,
            SolsticeMaskLocator._DRAW_DB_CLASSIFICATION_
        )
    except Exception:
        OpenMaya.MGlobal.displayError('Failed to register node: {}'.format(SolsticeMaskLocator._NAME_))

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            SolsticeMaskLocator._DRAW_DB_CLASSIFICATION_,
            SolsticeMaskLocator._DRAW_REGISTRANT_ID_,
            SolsticeMaskDrawOverride.creator
        )
    except Exception:
        OpenMaya.MGlobal.displayError('Failed to register draw override: {}'.format(SolsticeMaskDrawOverride._NAME_))


def uninitializePlugin(obj):
    plugin_fn = OpenMaya.MFnPlugin(obj)
    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            SolsticeMaskLocator._DRAW_DB_CLASSIFICATION_,
            SolsticeMaskLocator._DRAW_REGISTRANT_ID_
        )
    except Exception:
        OpenMaya.MGlobal.displayError('Failed to deregister draw override: {}'.format(SolsticeMaskDrawOverride._NAME_))

    try:
        plugin_fn.deregisterNode(SolsticeMaskLocator._ID_)
    except Exception:
        OpenMaya.MGlobal.displayError('Failed to unregister node: {}'.format(SolsticeMaskLocator._NAME_))

# ==================================================================================================================


def run():
    win = SolsticePlayBlast().show()
