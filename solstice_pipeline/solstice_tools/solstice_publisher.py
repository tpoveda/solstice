#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_publisher.py
# by Tomas Poveda
# Tool that is used to publish assets and sequences
# ______________________________________________________________________
# ==================================================================="""

import os
import weakref

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

import solstice_pipeline as sp
from solstice_gui import solstice_dialog, solstice_splitters
from solstice_utils import solstice_image as img
from solstice_utils import solstice_artella_utils as artella
from resources import solstice_resource


class SolsticePublisher(solstice_dialog.Dialog, object):

    name = 'Publisher'
    title = 'Solstice Tools - Publisher'
    version = '1.0'
    docked = False

    def __init__(self, name='PublisherWindow', asset=None, parent=None, **kwargs):
        self._asset = asset

        super(SolsticePublisher, self).__init__(name=name, parent=parent, **kwargs)

        self.setMaximumWidth(200)

    def custom_ui(self):
        super(SolsticePublisher, self).custom_ui()
        self.set_logo('solstice_publisher_logo')
        if self._asset:
            asset_publisher = AssetPublisherWidget(asset=self._asset)
            self.main_layout.addWidget(asset_publisher)


class AssetPublisherWidget(QWidget, object):
    def __init__(self, asset, parent=None):
        super(AssetPublisherWidget, self).__init__(parent=parent)

        self._asset = weakref.ref(asset)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        self._asset_icon = QLabel()
        self._asset_icon.setPixmap(
        solstice_resource.pixmap('empty_file', category='icons').scaled(200, 200, Qt.KeepAspectRatio))
        self._asset_icon.setAlignment(Qt.AlignCenter)
        if asset.icon:
            self._asset_icon.setPixmap(QPixmap.fromImage(img.base64_to_image(asset._icon, image_format=asset._icon_format)).scaled(300, 300, Qt.KeepAspectRatio))
        self._asset_label = QLabel(asset.name)
        self._asset_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self._asset_icon)
        main_layout.addWidget(self._asset_label)
        main_layout.addLayout(solstice_splitters.SplitterLayout())

        self._versions = self._asset().get_max_published_versions(all_versions=True)

        versions_layout = QGridLayout()
        versions_layout.setContentsMargins(10, 10, 10, 10)
        versions_layout.setSpacing(5)
        main_layout.addLayout(versions_layout)

        self._ui = dict()

        for i, category in enumerate(sp.valid_categories):
            self._ui[category] = dict()
            self._ui[category]['label'] = QLabel(category.upper())
            self._ui[category]['current_version'] = QLabel('v0')
            self._ui[category]['current_version'].setAlignment(Qt.AlignCenter)
            self._ui[category]['separator'] = QLabel()
            self._ui[category]['separator'].setPixmap(solstice_resource.pixmap('arrow_material', category='icons').scaled(QSize(24, 24)))
            self._ui[category]['next_version'] = QLabel('v0')
            self._ui[category]['next_version'].setAlignment(Qt.AlignCenter)
            self._ui[category]['check'] = QCheckBox('')
            self._ui[category]['check'].setChecked(True)
            self._ui[category]['check'].toggled.connect(self._update_versions)
            for j, widget in enumerate(['label', 'current_version', 'separator', 'next_version', 'check']):
                versions_layout.addWidget(self._ui[category][widget], i, j)

        for widget in ['label', 'current_version', 'separator', 'next_version', 'check']:
            self._ui['model'][widget].setVisible(self._asset().has_model())
            self._ui['shading'][widget].setVisible(self._asset().has_shading())
            self._ui['textures'][widget].setVisible(self._asset().has_textures())
            self._ui['groom'][widget].setVisible(self._asset().has_groom())

        main_layout.addWidget(solstice_splitters.Splitter('Comment'))
        self._comment_box = QTextEdit()
        self._comment_box.textChanged.connect(self._update_ui)
        main_layout.addWidget(self._comment_box)

        main_layout.addLayout(solstice_splitters.SplitterLayout())
        self._publish_btn = QPushButton('Publish')
        self._publish_btn.clicked.connect(self._publish)
        main_layout.addWidget(self._publish_btn)

        self._update_versions()

        # =====================================================================================================

        for cat in sp.valid_categories:
            asset_is_locked, current_user = self._asset().is_locked(category=cat, status='working')
            if asset_is_locked:
                if not current_user:
                    self._ui[cat]['check'].setChecked(False)
                    self._ui[cat]['current_version'].setText('LOCK')
                    self._ui[cat]['next_version'].setText('LOCK')
                    for name, w in self._ui[cat].items():
                        w.setEnabled(False)

    def _update_versions(self):
        for cat, version in self._versions.items():
            if version is None:
                curr_version_text = 'None'
                if self._ui[cat]['check'].isChecked():
                    next_version_text = 'v1'
                else:
                    next_version_text = 'None'
            else:
                curr_version_text = 'v{0}'.format(version[0])
                if self._ui[cat]['check'].isChecked():
                    next_version_text = 'v{0}'.format(int(version[0])+1)
                else:
                    next_version_text = 'v{0}'.format(version[0])
            self._ui[cat]['current_version'].setText(curr_version_text)
            self._ui[cat]['next_version'].setText(next_version_text)

        self._update_ui()

    def _update_ui(self):
        publish_state = True

        if not self._asset().has_groom():
            if not self._ui['model']['check'].isChecked() and not self._ui['shading']['check'].isChecked() and not self._ui['textures']['check'].isChecked():
                publish_state = False
        else:
            if not self._ui['model']['check'].isChecked() and not self._ui['shading']['check'].isChecked() and not self._ui['textures']['check'].isChecked() and not self._ui['groom']['check']:
                publish_state = False

        if self._comment_box.toPlainText() is None or self._comment_box.toPlainText() == '':
            publish_state = False

        self._publish_btn.setEnabled(publish_state)

    def _publish(self):

        max_versions = self._asset().get_max_versions(status='working')
        server_versions = max_versions['server']

        for cat in sp.valid_categories:
            if not self._ui[cat]['check'].isChecked():
                continue
            if not self._asset().has_category(category=cat):
                continue

            version_info = server_versions[cat]

            # TODO: When publishing shading files check that exists a Maya file that ends with
            # TODO: _SHD. If not, we avoid the publication of that file because nomenclature is not
            # TODO: valid

            asset_path = self._asset().asset_path
            new_version = int(self._ui[cat]['next_version'].text()[1:])
            new_version = '{0:03}'.format(new_version)
            asset_path = os.path.join(asset_path, '__{0}_v{1}__ '.format(cat, new_version))

            comment = self._comment_box.toPlainText()
            selected_version = dict()

            if cat == 'textures':
                textures_path = os.path.join(self._asset().asset_path, '__working__', 'textures')
                if os.path.exists(textures_path):
                    textures = [os.path.join(textures_path, f) for f in os.listdir(textures_path) if os.path.isfile(os.path.join(textures_path, f))]
                    if len(textures) <= 0:
                        continue
                    for txt in textures:
                        txt_history = artella.get_asset_history(txt)
                        txt_last_version = txt_history.versions[-1][0]
                        selected_version['textures/{0}'.format(os.path.basename(txt))] = int(txt_last_version)
            else:
                if not version_info:
                    selected_version[os.path.join(cat, self._asset().name + '.ma')] = 1
                else:
                    selected_version[version_info.relative_path] = version_info.version

            artella.publish_asset(file_path=asset_path, comment=comment, selected_versions=selected_version)


def run(asset=None):
    publisher_dialog = SolsticePublisher(asset=asset)
    publisher_dialog.exec_()