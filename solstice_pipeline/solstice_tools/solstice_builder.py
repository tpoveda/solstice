#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_builder.py
# by Tomas Poveda
# Custom QWidget that shows Solstice Assets in the Solstice Asset Viewer
# ______________________________________________________________________
# ==================================================================="""

import os
import json

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *

import solstice_pipeline as sp
from solstice_gui import solstice_windows
from solstice_gui import solstice_splitters
from solstice_utils import solstice_image as img


class SolsticeBuilder(solstice_windows.Window, object):

    name = 'SolsticeAssetBuilder'
    title = 'Solstice Tools - Solstice Builder'
    version = '1.1'

    def __init__(self):
        super(SolsticeBuilder, self).__init__()

        self.set_logo('solstice_assetbuilder_logo')

        self.resize(300, 500)

        tab_widget = QTabWidget()
        self.main_layout.addWidget(tab_widget)

        self._asset_builder = AssetBuilder()
        self._user_builder = UserBuilder()
        self._light_rig_builder = LightRigBuilder()
        self._sequence_builder = SequenceBuilder()
        self._shot_builder = ShotBuilder()
        tab_widget.addTab(self._asset_builder, 'Asset')
        tab_widget.addTab(self._sequence_builder, 'Sequence')
        tab_widget.addTab(self._shot_builder, 'Shot')
        tab_widget.addTab(self._user_builder, 'User')
        tab_widget.addTab(self._light_rig_builder, 'Light Rig')


class BuilderWidget(QWidget, object):
    def __init__(self, name='Asset', parent=None):
        super(BuilderWidget, self).__init__(parent=parent)

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(2, 2, 2, 2)
        base_layout.setSpacing(2)
        self.setLayout(base_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        base_layout.addLayout(self.main_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(2, 2, 2, 2)
        bottom_layout.setSpacing(2)
        base_layout.addLayout(solstice_splitters.SplitterLayout())
        base_layout.addLayout(bottom_layout)

        self.save_btn = QPushButton('Generate {} File'.format(name))
        self.load_btn = QPushButton('Load {} File'.format(name))
        bottom_layout.addWidget(self.save_btn)
        bottom_layout.addWidget(self.load_btn)

        self.save_btn.clicked.connect(self.save)
        self.load_btn.clicked.connect(self.load)

    def save(self):
        pass

    def load(self):
        pass


class AssetBuilder(BuilderWidget, object):
    def __init__(self, parent=None):
        super(AssetBuilder, self).__init__(parent=parent)

        self._current_icon_path = None
        self._current_preview_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._preview_btn = QPushButton('Preview')
        self._preview_btn.setMinimumSize(QSize(150, 150))
        self._preview_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._description_text = QTextEdit()
        self._description_text.setPlaceholderText('Description')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(5, 5, 5, 10)
        self.main_layout.addLayout(preview_layout)
        preview_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        preview_layout.addWidget(self._preview_btn, Qt.AlignCenter)
        preview_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self._description_text)

        self.main_layout.addItem(QSpacerItem(0, 5))

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)
        self._preview_btn.clicked.connect(self._set_preview)

    def save(self):
        out_dict = dict()
        out_dict['asset'] = dict()
        if self._current_icon_path and os.path.isfile(self._current_icon_path):
            image_format = os.path.splitext(self._current_icon_path)[1][1:].upper()
            icon_out = img.image_to_base64(image_path=self._current_icon_path, image_format=image_format)
            out_dict['asset']['icon'] = icon_out
            out_dict['asset']['icon_format'] = image_format
        out_dict['asset']['preview'] = ''
        out_dict['asset']['preview_format'] = ''
        out_dict['asset']['description'] = self._description_text.toPlainText()

        save_file = QFileDialog.getSaveFileName(self, 'Set folder to store asset data', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.exists(os.path.dirname(save_file)):
            with open(save_file, 'w') as f:
                json.dump(out_dict, f)

            # try:
            #     import subprocess
            #     subprocess.Popen(r'explorer /select,"{0}"'.format(save_file))
            # except Exception:
            #     pass

    def load(self):
        load_file = QFileDialog.getOpenFileName(self, 'Select asset data file to open', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.isfile(load_file):
            data = None
            with open(load_file, 'r') as f:
                data = json.load(f)
            if data:
                asset_icon = data['asset']['icon']
                icon_format = data['asset']['icon_format']
                asset_preview = data['asset']['preview']
                preview_format = data['asset']['preview_format']

                if asset_icon is not None and asset_icon != '':
                    asset_icon = asset_icon.encode('utf-8')
                    self._icon_btn.setIcon(QPixmap.fromImage(img.base64_to_image(asset_icon)))
                    self._icon_btn.setText('')
                if asset_preview is not None and asset_preview != '':
                    asset_preview = asset_preview.encode('utf-8')
                    self._preview_btn.setIcon(img.base64_to_icon(asset_preview, icon_format='PNG'))
                    self._preview_btn.setText('')
                self._description_text.setText(data['asset']['description'])

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Icon File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]

    def _set_preview(self):
        pass


class UserBuilder(BuilderWidget, object):
    def __init__(self, parent=None):
        super(UserBuilder, self).__init__(name='User', parent=parent)

        self._current_icon_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self.id_text = QTextEdit()
        self.id_text.setPlaceholderText('ID')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self.id_text)

        self.main_layout.addItem(QSpacerItem(0, 5))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Icon File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]


class LightRigBuilder(BuilderWidget, object):
    def __init__(self, parent=None):
        super(LightRigBuilder, self).__init__(name='Light Rig', parent=parent)

        self._current_icon_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._description_text = QTextEdit()
        self._description_text.setPlaceholderText('Description')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self._description_text)

        self.main_layout.addItem(QSpacerItem(0, 5))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Icon File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]


class SequenceBuilder(BuilderWidget, object):
    def __init__(self, parent=None):
        super(SequenceBuilder, self).__init__(name='Sequence', parent=parent)

        self._current_icon_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._description_text = QTextEdit()
        self._description_text.setPlaceholderText('Description')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self._description_text)

        self.main_layout.addItem(QSpacerItem(0, 5))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)

    def save(self):
        out_dict = dict()
        out_dict['sequence'] = dict()
        if self._current_icon_path and os.path.isfile(self._current_icon_path):
            image_format = os.path.splitext(self._current_icon_path)[1][1:].upper()
            icon_out = img.image_to_base64(image_path=self._current_icon_path, image_format=image_format)
            out_dict['sequence']['icon'] = icon_out
            out_dict['sequence']['icon_format'] = image_format
        out_dict['sequence']['description'] = self._description_text.toPlainText()

        save_file = QFileDialog.getSaveFileName(self, 'Set folder to store shot/sequence data', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.exists(os.path.dirname(save_file)):
            with open(save_file, 'w') as f:
                json.dump(out_dict, f)

            # try:
            #     import subprocess
            #     subprocess.Popen(r'explorer /select,"{0}"'.format(save_file))
            # except Exception:
            #     pass

    def load(self):
        print('loading')
        # load_file = QFileDialog.getOpenFileName(self, 'Select asset data file to open', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        # if os.path.isfile(load_file):
        #     data = None
        #     with open(load_file, 'r') as f:
        #         data = json.load(f)
        #     if data:
        #         asset_icon = data['asset']['icon']
        #         icon_format = data['asset']['icon_format']
        #         asset_preview = data['asset']['preview']
        #         preview_format = data['asset']['preview_format']
        #
        #         if asset_icon is not None and asset_icon != '':
        #             asset_icon = asset_icon.encode('utf-8')
        #             self._icon_btn.setIcon(QPixmap.fromImage(img.base64_to_image(asset_icon)))
        #             self._icon_btn.setText('')
        #         if asset_preview is not None and asset_preview != '':
        #             asset_preview = asset_preview.encode('utf-8')
        #             self._preview_btn.setIcon(img.base64_to_icon(asset_preview, icon_format='PNG'))
        #             self._preview_btn.setText('')
        #         self._description_text.setText(data['asset']['description'])

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Preview File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]


class ShotBuilder(BuilderWidget, object):
    def __init__(self, parent=None):
        super(ShotBuilder, self).__init__(name='Shot', parent=parent)

        self._current_icon_path = None

        self._icon_btn = QPushButton('Icon')
        self._icon_btn.setMinimumSize(QSize(150, 150))
        self._icon_btn.setMaximumSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._icon_btn.setIconSize(QSize(150, 150))
        self._description_text = QTextEdit()
        self._description_text.setPlaceholderText('Description')

        icon_layout = QHBoxLayout()
        icon_layout.setContentsMargins(5, 10, 5, 5)
        self.main_layout.addLayout(icon_layout)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        icon_layout.addWidget(self._icon_btn, Qt.AlignCenter)
        icon_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self.main_layout.addWidget(self._description_text)

        self.main_layout.addItem(QSpacerItem(0, 5))
        self.main_layout.addLayout(solstice_splitters.SplitterLayout())

        # ============================================================================

        self._icon_btn.clicked.connect(self._set_icon)

    def save(self):
        out_dict = dict()
        out_dict['shot'] = dict()
        if self._current_icon_path and os.path.isfile(self._current_icon_path):
            image_format = os.path.splitext(self._current_icon_path)[1][1:].upper()
            icon_out = img.image_to_base64(image_path=self._current_icon_path, image_format=image_format)
            out_dict['shot']['icon'] = icon_out
            out_dict['shot']['icon_format'] = image_format
        out_dict['shot']['description'] = self._description_text.toPlainText()

        save_file = QFileDialog.getSaveFileName(self, 'Set folder to store shot/sequence data', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        if os.path.exists(os.path.dirname(save_file)):
            with open(save_file, 'w') as f:
                json.dump(out_dict, f)

            # try:
            #     import subprocess
            #     subprocess.Popen(r'explorer /select,"{0}"'.format(save_file))
            # except Exception:
            #     pass

    def load(self):
        print('loading')
        # load_file = QFileDialog.getOpenFileName(self, 'Select asset data file to open', sp.get_solstice_assets_path(), 'JSON Files (*.json)')[0]
        # if os.path.isfile(load_file):
        #     data = None
        #     with open(load_file, 'r') as f:
        #         data = json.load(f)
        #     if data:
        #         asset_icon = data['asset']['icon']
        #         icon_format = data['asset']['icon_format']
        #         asset_preview = data['asset']['preview']
        #         preview_format = data['asset']['preview_format']
        #
        #         if asset_icon is not None and asset_icon != '':
        #             asset_icon = asset_icon.encode('utf-8')
        #             self._icon_btn.setIcon(QPixmap.fromImage(img.base64_to_image(asset_icon)))
        #             self._icon_btn.setText('')
        #         if asset_preview is not None and asset_preview != '':
        #             asset_preview = asset_preview.encode('utf-8')
        #             self._preview_btn.setIcon(img.base64_to_icon(asset_preview, icon_format='PNG'))
        #             self._preview_btn.setText('')
        #         self._description_text.setText(data['asset']['description'])

    def _set_icon(self):
        file_dialog = QFileDialog(self)
        icon_file_path = file_dialog.getOpenFileName(self, 'Select Preview File', sp.get_solstice_assets_path(), 'PNG Files (*.png);; JPG Files (*.jpg)')
        if icon_file_path and os.path.isfile(icon_file_path[0]):
            self._icon_btn.setIcon(QIcon(QPixmap(icon_file_path[0])))
            self._icon_btn.setText('')
            self._current_icon_path = icon_file_path[0]


def run():
    SolsticeBuilder().show()


