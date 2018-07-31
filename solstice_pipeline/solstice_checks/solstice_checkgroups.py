#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_checkgroups.py
# by Tomas Poveda
# Module that contains base class for creating sanity check groups
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_pipeline.solstice_checks import solstice_assetchecks

reload(solstice_assetchecks)


class SanityCheckGroup(QWidget, object):

    checkDone = Signal(object, bool)
    checkFinished = Signal(bool)
    checkBeingFixed = Signal()

    def __init__(self, name, auto_fix=False, stop_on_error=False, parent=None):
        super(SanityCheckGroup, self).__init__(parent=parent)

        self.name = name
        self.auto_fix = auto_fix
        self.stop_on_error = stop_on_error
        self.checks = list()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_widget.setLayout(self.scroll_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll_widget.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.main_layout.addWidget(scroll)

        self.check_btn = QPushButton('Check')
        self.main_layout.addWidget(self.check_btn)
        self.check_btn.clicked.connect(self._on_do_check)

    def add_check(self, check):
        check.image_lbl.setPixmap(check._wait_pixmap)
        if self.auto_fix:
            check.fix_btn.setVisible(False)
            check.fix_btn.setVisible(False)
            check.enable_check.setVisible(False)
            check.enable_check.setChecked(True)
            check.image_separator.setVisible(False)

        self.scroll_layout.addWidget(check)
        self.checks.append(check)

    def _on_do_check(self):

        valid_check = True

        for check in self.checks:
            if check.should_be_checked():
                valid_check = check.check()
                if valid_check:
                    check.valid_check()
                    self.checkDone.emit(check, True)
                else:
                    if self.auto_fix:
                        curr_text = check.check_text.text()
                        check.check_text.setText('Fixing ...')
                        check.fixing_check()
                        self.checkBeingFixed.emit()
                        valid_check = check.fix()
                        check.check_text.setText(curr_text)
                        if valid_check:
                            check.valid_check()
                            self.checkDone.emit(check, True)
                            continue

                    check.invalid_check()
                    if not self.auto_fix:
                        check.show_fix_button()
                    self.checkDone.emit(check, False)
                    if self.stop_on_error:
                        break
                    valid_check = False

        self.checkFinished.emit(valid_check)


class GeneralSanityCheck(SanityCheckGroup, object):
    def __init__(self, auto_fix=False, stop_on_error=False, parent=None):
        super(GeneralSanityCheck, self).__init__(name='General', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        # self.add_check(solstice_studentcheck.StudentLicenseCheck())


class ModelRigSanityCheck(SanityCheckGroup, object):
    def __init__(self, auto_fix=False, stop_on_error=False, parent=None):
        super(ModelRigSanityCheck, self).__init__(name='ModelRig', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)


class ShadingSanityCheck(SanityCheckGroup, object):
    def __init__(self, auto_fix=False, stop_on_error=False, parent=None):
        super(ShadingSanityCheck, self).__init__(name='Shading', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)


class TexturesSanityCheck(SanityCheckGroup, object):
    def __init__(self, asset, auto_fix=False, stop_on_error=False, parent=None):
        super(TexturesSanityCheck, self).__init__(name='Textures', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)


class AssetShadingPublishSantiyCheck(SanityCheckGroup, object):
    def __init__(self, asset, file_type, auto_fix=False, stop_on_error=False, parent=None):
        super(AssetShadingPublishSantiyCheck, self).__init__(name='AssetPublish', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        self.add_check(solstice_assetchecks.StudentLicenseCheck(asset=asset, status='working', file_type=file_type))
        self.add_check(solstice_assetchecks.ValidPublishedTextures(asset=asset, auto_fix=self.auto_fix))
        self.add_check(solstice_assetchecks.AssetFileSync(asset=asset, status='working', file_type=file_type, auto_fix=self.auto_fix))
        self.add_check(solstice_assetchecks.NotLockedAsset(asset=asset, status='working', file_type=file_type, auto_fix=self.auto_fix))
        self.add_check(solstice_assetchecks.TexturesFolderSync(asset=asset, auto_fix=self.auto_fix))


class AssetModelPublishSanityCheck(SanityCheckGroup, object):
    def __init__(self, asset, file_type, auto_fix=False, stop_on_error=False, parent=None):
        super(AssetModelPublishSanityCheck, self).__init__(name='AssetPublish', auto_fix=auto_fix, stop_on_error=stop_on_error, parent=parent)

        self.add_check(solstice_assetchecks.AssetFileExists(asset=asset, status='working', file_type=file_type))
        self.add_check(solstice_assetchecks.StudentLicenseCheck(asset=asset, status='working', file_type=file_type))
        # self.add_check(solstice_assetchecks.ModelValidMainGroup(asset=asset, status='working', file_type=file_type, task=task))
